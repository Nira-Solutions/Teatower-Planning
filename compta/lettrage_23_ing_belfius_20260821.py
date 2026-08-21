# -*- coding: utf-8 -*-
"""
LETTRAGE ING + BELFIUS 21/08/2026

Demande Nicolas : "lettre tout ce que tu vois dans ING et Belfius. Tu sais quoi faire
pour les factures clients."

Perimetre : 107 lignes non lettrees sur les journaux 14 (ING) et 36 (Belfius) au 21/08/2026.

Regle d'ecart (feedback_compta_ecart_reglement_tolerance) :
  |ecart| <= 5,00 EUR -> lettrage + write-off 657100 / 757100
  |ecart| >  5,00 EUR -> lettrage PARTIEL explicite (allow_partial), jamais de write-off

Types de traitement :
  A MATCH    : repointage 499000 -> 400000/440000 + reconcile sur la piece identifiee
  B TRANSIT  : repointage 499000 -> compte etabli, sans lettrage (acompte / double paiement)
  E AML      : repointage 499000 -> compte donne + reconcile contre une ligne existante

NOTE CONFIDENTIALITE : repo PUBLIC, pas de secret ici (ODOO_PWD en variable d'env).

Usage : python lettrage_23_ing_belfius_20260821.py            (DRY-RUN)
        python lettrage_23_ing_belfius_20260821.py --apply
"""

import os
import sys
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
if not PWD:
    raise SystemExit("Definir ODOO_PWD avant d'executer (creds dans Materiel TT.xlsx).")

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m_obj = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return m_obj.execute_kw(DB, uid, PWD, model, method, args, kw or {})


ACC_499000 = 221   # suspense bancaire
ACC_400000 = 162   # clients
ACC_440000 = 192   # fournisseurs
ACC_580000 = 233   # Internal Transfers of Funds (reconcile=True)
ACC_580001 = 819   # Compte de transfert Banque (reconcile=False)
ACC_580003 = 821   # Paiement Sodexo-Edenred (titres-repas)
ACC_580004 = 1225  # Bons cadeaux Smartbox
ACC_551102 = 811   # Pmt a recevoir Mollie (reconcile=True)
ACC_657100 = 293   # Negative Payment Differences
ACC_757100 = 347   # Positive Payment Differences
JOURNAL_MISC = 11
TODAY = "2026-08-21"
ECART_TOLERANCE = 5.00

P_SIPS = 110685    # S.I.P.S. ASBL

DRY = "--apply" not in sys.argv

# ---------------------------------------------------------------------------
# A -- pieces identifiees
# ---------------------------------------------------------------------------
CASES_MATCH = [
    # --- CLIENTS : communication structuree = payment_reference de la facture (cle maitre)
    {"bsl_ids": [20444], "acc": ACC_400000, "docs": ["INV/2026/03857"],
     "label": "ALIVIM / Spar Gembloux 531,01 - comm 000/0044/47347 (exact)"},
    {"bsl_ids": [20468], "acc": ACC_400000, "docs": ["INV/2026/03550"],
     "label": "PURE BASTOGNE / Hello Bio 346,39 - comm 000/0042/74363 (exact)"},
    {"bsl_ids": [20443], "acc": ACC_400000, "docs": ["INV/2026/03814"],
     "label": "GEMBLOUXIM / Intermarche Gembloux 478,78 vs 478,80 - comm 000/0044/25018 (ecart -0,02)"},
    {"bsl_ids": [20480], "acc": ACC_400000, "docs": ["INV/2026/03513"],
     "label": "MARER / AD Delhaize Bastogne 465,51 vs 465,50 - comm 000/0042/64461 (ecart +0,01)"},

    # --- FOURNISSEURS : comm structuree ou reference de facture citee dans le libelle
    {"bsl_ids": [20417], "acc": ACC_440000, "docs": ["RESA1251"],
     "label": "EZCharge/EasyPlug 210,56 - comm 200/0003/95041 = payment_reference RESA1251 (exact)"},
    {"bsl_ids": [20418], "acc": ACC_440000, "docs": ["RESA1229"],
     "label": "EZCharge/EasyPlug 145,20 - comm 000/0274/37761 = payment_reference RESA1229 (exact)"},
    {"bsl_ids": [20271], "acc": ACC_440000, "docs": ["RESA1236"],
     "label": "Shyfter 47,19 - libelle carte 'INVOICE 2026080556' = ref RESA1236 (exact)"},
    # Belfius facture ses frais de compte : la facture du 1er du mois est prelevee vers le 5.
    {"bsl_ids": [19185], "acc": ACC_440000, "docs": ["RESA1046"],
     "label": "Belfius frais expedition avis 04/06 6,16 -> RESA1046 (01/06, montant unique)"},
    {"bsl_ids": [19535], "acc": ACC_440000, "docs": ["RESA1177"],
     "label": "Belfius frais expedition avis 06/07 12,32 -> RESA1177 (01/07)"},
    {"bsl_ids": [19536], "acc": ACC_440000, "docs": ["RESA1178"],
     "label": "Belfius Business Pack Plus 06/07 7,67 -> RESA1178 (01/07)"},
    {"bsl_ids": [20186], "acc": ACC_440000, "docs": ["RESA1250"],
     "label": "Belfius frais expedition avis 06/08 12,32 -> RESA1250 (01/08)"},
    {"bsl_ids": [20187], "acc": ACC_440000, "docs": ["RESA1260"],
     "label": "Belfius Business Pack Plus 06/08 7,67 -> RESA1260 (01/08)"},
]

# ---------------------------------------------------------------------------
# B -- repointage sans lettrage
# ---------------------------------------------------------------------------
CASES_TRANSIT = [
    # SIPS ASBL : facture INV1/26-27/0032 (20,00, comm 000/0044/28149) DEJA payee en especes
    # a la caisse Liege le 11/08 (POSS/26-27/08/0055). Le virement du 17/08 est un 2e paiement
    # -> credit ouvert sur le compte client, PAS de lettrage (cf reference_lettrage_ing_methode).
    {"bsl": 20428, "acc": ACC_400000, "partner": P_SIPS,
     "label": "S.I.P.S. ASBL 20,00 - double paiement (facture deja soldee en especes caisse Liege)"},
]

# ---------------------------------------------------------------------------
# E -- lettrage contre une ligne comptable existante (pas une facture)
# ---------------------------------------------------------------------------
CASES_AML = [
    # RESA1230 Nira Solutions 8.742,25 a ete payee via un "paiement manuel" enregistre dans le
    # journal MOLLIE (MOL/26-27/0345) : la contrepartie dort sur 551102 alors que l'argent est
    # sorti de l'ING. On solde 551102 avec la ligne bancaire -> 551102 revient a 0, RESA1230
    # reste paid. Aucun impact resultat.
    {"bsl": 20474, "acc": ACC_551102, "aml": 203858, "partner": None,
     "label": "Nira Solutions -8.742,25 - solde le 551102 laisse par MOL/26-27/0345 (RESA1230)"},
]

# ---------------------------------------------------------------------------
NON_TRAITES = [
    ("ING  20156 / 20425", "CARREFOUR   +4.862,06 / +1.396,75", "71 factures ouvertes (28.744,02) : 0 solution pour 4.862,06, 8+ solutions non uniques pour 1.396,75 -> exiger l'avis de paiement"),
    ("ING  20381", "DELHAIZE LE LION       +2.652,97", "90 factures ouvertes (52.175,73), 7+ combinaisons possibles -> exiger l'avis"),
    ("ING  19660 / 20373", "ITM ALIMENTAIRE  +637,24 / +160,61", "24 factures Intermarche ouvertes, aucune combinaison exacte <=4 factures -> exiger l'avis"),
    ("ING  19625", "KIRCHNER domiciliation -12.837,54", "aucune combinaison exacte sur les factures Mount Everest / Kirchner -> exiger l'Avis"),
    ("BELF 20352", "KIRCHNER clearing     -49.551,11", "idem, exiger le detail du clearing"),
    ("BELF 19188", "PAIEMENT DU PRET      +30.000,00", "tirage credit Belfius 071-9574936-30 -> imputation 174xxx a arbitrer"),
    ("BELF 20350", "NIRA SOLUTIONS        +10.000,00", "pret actionnaire -> 416100 / 424xxx a arbitrer"),
    ("BELF 20353", "TILMAN JEAN NOEL      +30.000,00", "pret actionnaire -> 424002 Emprunt Jean-Noel Tilman a confirmer"),
    ("BELF x14", "CHARGES ECHUES CREDIT PRO", "706,91 / 273,64 / 410,46 / 2.559,85 : tableau d'amortissement necessaire (split capital/interets)"),
    ("BELF 18034/18036/18038/18360/19184", "TENUE DE COMPTE -4,42 x5", "les 3 factures Belfius ouvertes a 5,14 (RESA832/894/1047) ne correspondent pas au montant preleve"),
    ("BELF 18037/18039", "EXPEDITION AVIS -3,08 x2", "pas de facture Belfius ouverte a ce montant"),
    ("BELF 18046/19839", "BUSINESS CASH PLUS -15,00 x2", "pas de facture enregistree"),
    ("BELF 18047/19190", "FRAIS DE DOSSIER CREDIT -250,00 x2", "a immobiliser ou charger -> arbitrage"),
    ("BELF 19570/19571", "COMMISSION 39,83 / INTERETS 0,64", "pas de facture enregistree"),
    ("BELF 19640/19641", "MOLLIE verification -0,01 x2", "micro-debits de verification de compte, pas un reglement"),
    ("BELF 19959", "NOTAIRE PIRET-GERARD    -492,59", "aucune facture enregistree (dossier 4586/002)"),
    ("BELF 19999/20125/20126/20213", "PETITS ACHATS CARTE Stephan", "Meta Ads, Familia, CRF Express, Get your mug : notes de frais a saisir"),
    ("BELF 20157 + ING 20288/19735/20087", "SALAIRES ET AVANCES", "OD de paie a controler avant tout lettrage (cf project_salaires_non_comptabilises_juin_juillet_2026)"),
    ("ING  19610/19737/19738/19739/20390/20391/20392", "AVANCES SALAIRES / MARKETING", "Vansimpsen, van Ooteghem, Cabosart, Claeys : rattacher aux OD de paie / notes de frais"),
    ("ING  19746 / 20276", "DOUANES ET ACCISES -1.040,40 / -699,00", "970AI8902/F : aucune piece enregistree"),
    ("ING  20208", "OSS TVA Q2.2026          -296,14", "declaration OSS -> compte TVA a arbitrer"),
    ("ING  20049", "CHEQUE GUICHET           -396,00", "aucun libelle exploitable, piece a retrouver"),
    ("ING  19871 / 19985 / 19944", "RADIUS -308,80 / -459,81 - PROXIMUS -200,00", "lettrages croises a defaire (factures deja lettrees contre des lignes bancaires d'autres mois) - hors perimetre"),
    ("ING  19780 / 20178", "SENDCLOUD  -24,45 / -121,00", "aucune facture d'achat enregistree (1-26-BE0060716 / BE0064771)"),
    ("ING  divers", "GOOGLE / ADOBE / INTUIT / SHOPIFY / META / FAIRE", "domiciliations et achats carte sans facture d'achat enregistree en compta"),
    ("ING  19992", "iPiD Europe                +0,01", "micro-depot de verification de compte"),
    ("ING  20420", "CILE eau                  -59,00", "pas de facture enregistree"),
    ("ING  19804 / 20414", "MASTERCARD ING -755,90 / -999,74", "releve de carte : contrepartie des achats carte, a solder quand les notes de frais seront saisies"),
    ("ALERTE", "SHYFTER doublon", "RESA1020 et RESA1089 portent la MEME ref 2026060567 (47,19) : facture d'achat encodee 2x, a extourner"),
]

# ---------------------------------------------------------------------------
# Helpers (repris de lettrage_18/20)
# ---------------------------------------------------------------------------
def get_bsl(bsl_id):
    rows = call("account.bank.statement.line", "read", [[bsl_id]],
                {"fields": ["move_id", "is_reconciled", "amount", "partner_id", "payment_ref", "journal_id"]})
    if not rows:
        return None
    bsl = rows[0]
    mid = bsl["move_id"][0] if bsl.get("move_id") else None
    bsl["_move_id"] = mid
    if mid:
        mv = call("account.move", "read", [[mid]], {"fields": ["state", "name", "line_ids"]})[0]
        bsl["_move_state"] = mv["state"]
        bsl["_move_name"] = mv["name"]
        bsl["_line_ids"] = mv["line_ids"]
    return bsl


def get_move_lines(ids, fields=None):
    if not ids:
        return []
    flds = fields or ["id", "account_id", "partner_id", "debit", "credit",
                      "amount_residual", "reconciled", "move_id"]
    return call("account.move.line", "read", [ids], {"fields": flds})


def find_suspense_line(line_ids):
    for ln in get_move_lines(line_ids):
        if (ln.get("account_id") or [None])[0] == ACC_499000:
            return ln
    return None


def get_doc(name):
    rows = call("account.move", "search_read", [[["name", "=", name]]],
                {"fields": ["id", "name", "payment_state", "amount_residual", "amount_total",
                            "move_type", "partner_id"]})
    return rows[0] if rows else None


def open_lines_on(move_id, acc):
    return call("account.move.line", "search_read",
                [[["move_id", "=", move_id], ["account_id", "=", acc], ["reconciled", "=", False]]],
                {"fields": ["id", "amount_residual", "debit", "credit", "partner_id"]})


def call_reconcile_safe(line_ids):
    """reconcile() renvoie parfois None -> Fault de marshalling alors que le lettrage a eu lieu."""
    try:
        res = call("account.move.line", "reconcile", [line_ids])
        return True, res
    except xmlrpc.client.Fault as f:
        msg = str(f.faultString)
        low = msg.lower()
        if "cannot marshal" in low or "marshaling" in low or "nonetype" in low:
            return True, "marshalling_false_fault_ignored"
        return False, msg


def create_writeoff(partner_id, amount_abs, debit_acc, credit_acc, label):
    vals = {
        "move_type": "entry",
        "journal_id": JOURNAL_MISC,
        "date": TODAY,
        "ref": f"Write-off ecart reglement lettrage ING/Belfius 21/08 - {label}",
        "line_ids": [
            (0, 0, {"account_id": debit_acc, "partner_id": partner_id,
                    "debit": round(amount_abs, 2), "credit": 0.0, "name": f"Ecart reglement {label}"}),
            (0, 0, {"account_id": credit_acc, "partner_id": partner_id,
                    "debit": 0.0, "credit": round(amount_abs, 2), "name": f"Ecart reglement {label}"}),
        ],
    }
    mid = call("account.move", "create", [vals])
    call("account.move", "action_post", [[mid]])
    mv = call("account.move", "read", [[mid]], {"fields": ["name", "line_ids"]})[0]
    return mid, mv["line_ids"], mv["name"]


# ---------------------------------------------------------------------------
def process_match(case):
    bsl_ids, acc, docs = case["bsl_ids"], case["acc"], case["docs"]
    label = case["label"]
    allow_partial = case.get("allow_partial", False)
    print("=" * 104)
    print(f"[MATCH] BSL {bsl_ids} -- {label}")
    result = {"bsl_ids": bsl_ids, "label": label, "status": None, "error": None, "writeoff_move": None}

    for bsl_id in bsl_ids:
        pre = get_bsl(bsl_id)
        if pre and pre["is_reconciled"]:
            print(f"  BSL {bsl_id} deja reconciliee -- SKIP")
            result["status"] = "SKIP_DEJA_RECONCILED"
            return result

    ref_doc = get_doc(docs[0])
    if not ref_doc:
        result["status"] = "ERROR"; result["error"] = f"Doc {docs[0]} introuvable"
        print("  ERREUR:", result["error"]); return result
    ref_lines = open_lines_on(ref_doc["id"], acc)
    if not ref_lines:
        result["status"] = "ERROR"; result["error"] = f"Aucune ligne {acc} ouverte sur {docs[0]}"
        print("  ERREUR:", result["error"]); return result
    partner_id = (ref_lines[0].get("partner_id") or [False])[0] or ref_doc["partner_id"][0]
    print(f"  partner de repointage = {partner_id}")

    bsl_aml_ids, total_bsl = [], 0.0
    for bsl_id in bsl_ids:
        bsl = get_bsl(bsl_id)
        if not bsl:
            result["status"] = "ERROR"; result["error"] = f"BSL {bsl_id} introuvable"
            print("  ERREUR:", result["error"]); return result
        if bsl.get("_move_state") != "posted":
            result["status"] = "ERROR"; result["error"] = f"BSL {bsl_id} move state={bsl.get('_move_state')}"
            print("  ERREUR:", result["error"]); return result
        total_bsl += bsl["amount"]
        susp = find_suspense_line(bsl.get("_line_ids", []))
        if not susp:
            already = [l for l in get_move_lines(bsl.get("_line_ids", []))
                       if (l.get("account_id") or [None])[0] == acc]
            if not already:
                result["status"] = "ERROR"
                result["error"] = f"BSL {bsl_id} : ni ligne 499000 ni ligne {acc}"
                print("  ERREUR:", result["error"]); return result
            bsl_line = already[0]
            print(f"  BSL {bsl_id} : ligne {acc} deja presente (id={bsl_line['id']})")
        elif DRY:
            print(f"  DRY   BSL {bsl_id} : ligne suspense {susp['id']} -> compte {acc} / partner {partner_id}")
            bsl_line = susp
        else:
            call("account.move.line", "write", [[susp["id"]], {"account_id": acc, "partner_id": partner_id}])
            bsl_line = get_move_lines([susp["id"]])[0]
            print(f"  BSL {bsl_id} : ligne suspense {susp['id']} repointee -> {acc} / partner {partner_id}")
        bsl_aml_ids.append(bsl_line["id"])

    doc_line_ids, total_docs, doc_names = [], 0.0, []
    for dname in docs:
        d = get_doc(dname)
        if not d:
            result["status"] = "ERROR"; result["error"] = f"Doc {dname} introuvable"
            print("  ERREUR:", result["error"]); return result
        if d["payment_state"] == "paid":
            print(f"    {dname} deja paid -- SKIP"); continue
        lines = open_lines_on(d["id"], acc)
        if not lines:
            result["status"] = "ERROR"; result["error"] = f"Pas de ligne {acc} ouverte pour {dname}"
            print("  ERREUR:", result["error"]); return result
        for l in lines:
            doc_line_ids.append(l["id"]); total_docs += l["amount_residual"]
        doc_names.append(dname)
        print(f"    {dname} : residual={d['amount_residual']:.2f} lignes={[l['id'] for l in lines]}")

    # cote fournisseur les residuels sont negatifs (credit) : on compare en valeur absolue
    ecart = round(abs(total_bsl) - abs(total_docs), 2)
    print(f"  BSL total={total_bsl:.2f} | docs total (signe)={total_docs:.2f} | ECART(abs)={ecart:+.2f}")

    if abs(ecart) > ECART_TOLERANCE and not allow_partial:
        result["status"] = "ERROR"
        result["error"] = f"Ecart {ecart:+.2f} > tolerance {ECART_TOLERANCE:.2f} sans allow_partial -- ABANDON"
        print("  ERREUR:", result["error"]); return result

    if DRY:
        print(f"  DRY   reconcile({bsl_aml_ids + doc_line_ids})")
        if allow_partial and abs(ecart) > ECART_TOLERANCE:
            print(f"  DRY   lettrage PARTIEL volontaire (ecart {ecart:+.2f}) -- pas de write-off")
        elif abs(ecart) >= 0.005:
            sens = "657100 (charge)" if ecart < 0 else "757100 (produit)"
            print(f"  DRY   write-off {abs(ecart):.2f} sur {sens}")
        result["status"] = "DRY"
        return result

    matching_ids = bsl_aml_ids + doc_line_ids
    ok, res = call_reconcile_safe(matching_ids)
    if not ok:
        result["status"] = "ERROR"; result["error"] = f"reconcile() echoue: {res}"
        print("  ERREUR:", result["error"]); return result
    print(f"  reconcile({matching_ids}) -> OK ({res})")

    if allow_partial and abs(ecart) > ECART_TOLERANCE:
        print(f"  Lettrage PARTIEL volontaire (ecart {ecart:+.2f}) -- pas de write-off")
    elif abs(ecart) >= 0.005:
        if ecart < 0:
            debit_acc, credit_acc = ACC_657100, acc
            print(f"  Ecart negatif -- write-off CHARGE 657100 {abs(ecart):.2f}")
        else:
            debit_acc, credit_acc = acc, ACC_757100
            print(f"  Ecart positif -- write-off PRODUIT 757100 {abs(ecart):.2f}")
        wo_id, wo_lines, wo_name = create_writeoff(partner_id, abs(ecart), debit_acc, credit_acc,
                                                   f"BSL{bsl_ids}/{label}")
        result["writeoff_move"] = wo_name
        print(f"  Write-off cree : {wo_name} (move_id={wo_id})")
        wo_target = [l for l in get_move_lines(wo_lines) if (l.get("account_id") or [None])[0] == acc]
        if wo_target:
            residual_open = call("account.move.line", "search_read",
                                 [[["id", "in", matching_ids], ["reconciled", "=", False]]],
                                 {"fields": ["id", "amount_residual"]})
            if residual_open:
                ids2 = [wo_target[0]["id"]] + [r["id"] for r in residual_open]
                ok2, res2 = call_reconcile_safe(ids2)
                if not ok2:
                    result["status"] = "ERROR"; result["error"] = f"reconcile write-off echoue: {res2}"
                    print("  ERREUR:", result["error"]); return result
                print(f"  reconcile write-off ({ids2}) -> OK")

    print("  --- VERIF ---")
    all_rec = True
    for b in bsl_ids:
        bc = get_bsl(b)
        print(f"   BSL {bc.get('_move_name')} is_reconciled={bc['is_reconciled']}")
        if not bc["is_reconciled"]:
            all_rec = False
    all_paid = True
    for dname in doc_names:
        dc = get_doc(dname)
        print(f"   {dname} payment_state={dc['payment_state']} residual={dc['amount_residual']:.2f}")
        if dc["payment_state"] not in ("paid", "reversed") and abs(dc["amount_residual"]) > 0.01 and not allow_partial:
            all_paid = False
    if all_rec and (all_paid or allow_partial):
        result["status"] = "OK"; print("  RESULTAT: OK")
    else:
        result["status"] = "WARN"; result["error"] = "BSL non reconciliee ou doc non solde"
        print("  RESULTAT: WARN --", result["error"])
    return result


def process_transit(case):
    """Repointage simple 499000 -> compte cible, sans lettrage."""
    bsl_id, acc, partner_id, label = case["bsl"], case["acc"], case.get("partner"), case["label"]
    print("=" * 104)
    print(f"[TRANSIT] BSL {bsl_id} -> compte {acc} -- {label}")
    result = {"bsl_ids": [bsl_id], "label": label, "status": None, "error": None, "writeoff_move": None}

    bsl = get_bsl(bsl_id)
    if not bsl:
        result["status"] = "ERROR"; result["error"] = "BSL introuvable"
        print("  ERREUR:", result["error"]); return result
    if bsl["is_reconciled"]:
        print("  deja reconciliee -- SKIP"); result["status"] = "SKIP_DEJA_RECONCILED"; return result
    if bsl.get("_move_state") != "posted":
        result["status"] = "ERROR"; result["error"] = f"move state={bsl.get('_move_state')}"
        print("  ERREUR:", result["error"]); return result

    susp = find_suspense_line(bsl.get("_line_ids", []))
    if not susp:
        result["status"] = "ERROR"; result["error"] = "pas de ligne 499000"
        print("  ERREUR:", result["error"]); return result

    vals = {"account_id": acc}
    if partner_id:
        vals["partner_id"] = partner_id
    if DRY:
        print(f"  DRY   ligne suspense {susp['id']} ({bsl['amount']:+.2f}) -> {vals}")
        result["status"] = "DRY"; return result

    call("account.move.line", "write", [[susp["id"]], vals])
    after = get_bsl(bsl_id)
    print(f"  ligne {susp['id']} repointee -> {vals} | is_reconciled={after['is_reconciled']}")
    result["status"] = "OK" if after["is_reconciled"] else "WARN"
    if not after["is_reconciled"]:
        result["error"] = "BSL toujours non reconciliee apres repointage"
    return result


def process_internal(pair):
    """Virement interne : les 2 lignes miroir -> 580000 puis lettrees entre elles."""
    a, b, label = pair["a"], pair["b"], pair["label"]
    print("=" * 104)
    print(f"[INTERNE] BSL {a} <-> {b} -- {label}")
    result = {"bsl_ids": [a, b], "label": f"VIREMENT INTERNE {label}", "status": None,
              "error": None, "writeoff_move": None}
    lines, total = [], 0.0
    for bid in (a, b):
        bsl = get_bsl(bid)
        if not bsl:
            result["status"] = "ERROR"; result["error"] = f"BSL {bid} introuvable"
            print("  ERREUR:", result["error"]); return result
        if bsl["is_reconciled"]:
            print(f"  BSL {bid} deja reconciliee -- SKIP")
            result["status"] = "SKIP_DEJA_RECONCILED"; return result
        total += bsl["amount"]
        susp = find_suspense_line(bsl.get("_line_ids", []))
        if not susp:
            result["status"] = "ERROR"; result["error"] = f"BSL {bid} : ligne 499000 introuvable"
            print("  ERREUR:", result["error"]); return result
        print(f"  BSL {bid} ({bsl['_move_name']}) amount={bsl['amount']:.2f} suspense aml={susp['id']} "
              f"D={susp['debit']:.2f} C={susp['credit']:.2f}")
        lines.append(susp["id"])
    if abs(total) > 0.005:
        result["status"] = "ERROR"; result["error"] = f"Somme des 2 lignes = {total:+.2f}, attendu 0,00 -- ABANDON"
        print("  ERREUR:", result["error"]); return result
    if DRY:
        print(f"  DRY   repointer {lines} -> 580000 puis reconcile")
        result["status"] = "DRY"; return result
    call("account.move.line", "write", [lines, {"account_id": ACC_580000}])
    print(f"  lignes {lines} repointees -> 580000 Internal Transfers of Funds")
    ok, res = call_reconcile_safe(lines)
    if not ok:
        result["status"] = "ERROR"; result["error"] = f"reconcile() echoue: {res}"
        print("  ERREUR:", result["error"]); return result
    print(f"  reconcile({lines}) -> OK ({res})")
    states = [(bid, get_bsl(bid)["is_reconciled"]) for bid in (a, b)]
    print("  --- VERIF ---", states)
    result["status"] = "OK" if all(s for _, s in states) else "WARN"
    if result["status"] == "WARN":
        result["error"] = "au moins une des 2 lignes reste non reconciliee"
    return result


def process_aml(case):
    """Repointage 499000 -> compte cible puis lettrage contre une ligne comptable existante."""
    bsl_id, acc, aml_id, label = case["bsl"], case["acc"], case["aml"], case["label"]
    partner_id = case.get("partner")
    print("=" * 104)
    print(f"[AML] BSL {bsl_id} -> compte {acc} <-> aml {aml_id} -- {label}")
    result = {"bsl_ids": [bsl_id], "label": label, "status": None, "error": None, "writeoff_move": None}

    bsl = get_bsl(bsl_id)
    if not bsl:
        result["status"] = "ERROR"; result["error"] = "BSL introuvable"
        print("  ERREUR:", result["error"]); return result
    if bsl["is_reconciled"]:
        print("  deja reconciliee -- SKIP"); result["status"] = "SKIP_DEJA_RECONCILED"; return result

    target = get_move_lines([aml_id])
    if not target:
        result["status"] = "ERROR"; result["error"] = f"aml {aml_id} introuvable"
        print("  ERREUR:", result["error"]); return result
    t = target[0]
    if t["reconciled"]:
        result["status"] = "ERROR"; result["error"] = f"aml {aml_id} deja lettree"
        print("  ERREUR:", result["error"]); return result
    if (t.get("account_id") or [None])[0] != acc:
        result["status"] = "ERROR"
        result["error"] = f"aml {aml_id} sur le compte {t.get('account_id')} != {acc}"
        print("  ERREUR:", result["error"]); return result
    print(f"  cible aml {aml_id} D={t['debit']:.2f} C={t['credit']:.2f} residual={t['amount_residual']:.2f}")

    susp = find_suspense_line(bsl.get("_line_ids", []))
    if not susp:
        result["status"] = "ERROR"; result["error"] = "pas de ligne 499000"
        print("  ERREUR:", result["error"]); return result

    # les 2 residuels doivent s'annuler (debit suspense vs credit de la ligne cible)
    ecart = round(susp["amount_residual"] + t["amount_residual"], 2)
    print(f"  suspense residual={susp['amount_residual']:.2f} | aml residual={t['amount_residual']:.2f} | somme={ecart:+.2f}")
    if abs(ecart) > 0.005:
        result["status"] = "ERROR"
        result["error"] = f"somme {ecart:+.2f} != 0,00 -- ABANDON"
        print("  ERREUR:", result["error"]); return result

    vals = {"account_id": acc}
    if partner_id:
        vals["partner_id"] = partner_id
    if DRY:
        print(f"  DRY   ligne suspense {susp['id']} -> {vals} puis reconcile([{susp['id']}, {aml_id}])")
        result["status"] = "DRY"; return result

    call("account.move.line", "write", [[susp["id"]], vals])
    ok, res = call_reconcile_safe([susp["id"], aml_id])
    if not ok:
        result["status"] = "ERROR"; result["error"] = f"reconcile() echoue: {res}"
        print("  ERREUR:", result["error"]); return result
    after = get_bsl(bsl_id)
    after_t = get_move_lines([aml_id])[0]
    print(f"  reconcile OK | BSL is_reconciled={after['is_reconciled']} | aml residual={after_t['amount_residual']:.2f}")
    result["status"] = "OK" if after["is_reconciled"] and abs(after_t["amount_residual"]) < 0.005 else "WARN"
    if result["status"] == "WARN":
        result["error"] = "BSL ou aml toujours ouvert"
    return result


if __name__ == "__main__":
    print("MODE:", "DRY-RUN (rien ecrit)" if DRY else "APPLY (ecriture reelle)")
    print(f"Tolerance write-off = {ECART_TOLERANCE:.2f} EUR (657100 / 757100)\n")
    results = []
    for c in CASES_MATCH:
        results.append(process_match(c))
    for c in CASES_TRANSIT:
        results.append(process_transit(c))
    for c in CASES_AML:
        results.append(process_aml(c))

    print("\n" + "=" * 104)
    print("RECAPITULATIF")
    print("=" * 104)
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(f" BSL {str(r['bsl_ids']):>14} | {r['label'][:70]:70} | {str(r['status']):22} "
              f"| wo={r.get('writeoff_move')} | {r.get('error') or ''}")
    print("\n ", counts)
    print("\n NON TRAITES (piece / arbitrage manquant) :")
    for ref, montant, why in NON_TRAITES:
        print(f"  {ref:38} {montant:38} {why}")
