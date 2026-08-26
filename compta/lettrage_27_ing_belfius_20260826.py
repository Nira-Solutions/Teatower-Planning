# -*- coding: utf-8 -*-
"""
LETTRAGE ING + BELFIUS 26/08/2026

Demande Nicolas : "lettre ING et Belfius".

Perimetre : journaux 14 (ING) et 36 (Belfius). 103 lignes non lettrees au 26/08/2026.
Seuls les cas CORROBORES sont traites (reference_lettrage_ing_methode) :
communication structuree > numero de piece > IBAN payeur + montant.

Regle d'ecart (feedback_compta_ecart_reglement_tolerance) :
  |ecart| <= 5,00 EUR -> lettrage + write-off 657100 / 757100
  |ecart| >  5,00 EUR -> lettrage PARTIEL explicite (allow_partial), jamais force

NOTE CONFIDENTIALITE : repo PUBLIC, pas de secret ici (ODOO_PWD en variable d'env).

Usage : python lettrage_27_ing_belfius_20260826.py            (DRY-RUN)
        python lettrage_27_ing_belfius_20260826.py --apply
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
ACC_657100 = 293   # Negative Payment Differences
ACC_757100 = 347   # Positive Payment Differences
JOURNAL_MISC = 11
TODAY = "2026-08-26"
ECART_TOLERANCE = 5.00

DRY = "--apply" not in sys.argv

# ---------------------------------------------------------------------------
# 0 -- facture fournisseur DRAFT a poster avant lettrage
#      move 45044 = Vilna Gaon S.R.L, ref INV/2026/00010, 2.000,00 TTC
#      (1.652,89 sur 616600 Frais de marketing + 347,11 TVA), echeance 25/08,
#      payment_reference +++000/0001/68132+++ = EXACTEMENT la comm structuree
#      du virement Belfius 20560 du 25/08. Piece presente, paiement fait :
#      il ne manque que la validation du brouillon.
# ---------------------------------------------------------------------------
DRAFT_BILLS_TO_POST = [
    {"move_id": 45044, "expected_total": 2000.00, "partner": 3286,
     "bsl": 20560,
     "label": "Vilna Gaon INV/2026/00010 2.000,00 - comm 000/0001/68132"},
]

# ---------------------------------------------------------------------------
# A -- pieces identifiees (lettrage)
# ---------------------------------------------------------------------------
CASES_MATCH = [
    # --- Clients : communication structuree = payment_reference de la facture ---
    # "***000/0044/83117***" -> INV/2026/03943 (Spar Clavier, res 332,50).
    # Payeur DELDIS SRL, IBAN BE24 0017 2866 9938, Clavier. Ecart +0,01.
    {"bsl_ids": [20541], "acc": ACC_400000, "docs": ["INV/2026/03943"],
     "label": "DELDIS / Spar Clavier 332,51 - comm 000/0044/83117 (ecart +0,01)"},

    # "+++000/0044/60279+++" -> INV/2026/03893 (SPRL Durant-Rabaey, res 789,63).
    # Payeur DURANT-RABAEY, IBAN BE70 5040 1700 7725. Ecart -0,02.
    {"bsl_ids": [20542], "acc": ACC_400000, "docs": ["INV/2026/03893"],
     "label": "DURANT-RABAEY 789,61 - comm 000/0044/60279 (ecart -0,02)"},

    # --- Fournisseur : paiement ONSS 116/5516/51214, 8.945,00 ---
    # Meme montant et meme reference ONSS que le paiement du 16/07 (BSL 19811),
    # qui avait ete lettre en 440000 / SD Worx Secretariat Social contre les
    # documents comptables 1BT1014 (RESA467 + RESA522), en FIFO.
    # On reproduit : FIFO sur les plus anciennes RESA ouvertes du meme fournisseur
    # -> RESA522 (solde 53,56) puis RESA713 (10.794,47) en PARTIEL.
    {"bsl_ids": [20562], "acc": ACC_440000, "docs": ["RESA522", "RESA713"],
     "allow_partial": True,
     "label": "ONSS 8.945,00 (116/5516/51214) - FIFO SD Worx RESA522+RESA713 (partiel)"},
]

# ---------------------------------------------------------------------------
# B -- repointage sans lettrage
# ---------------------------------------------------------------------------
CASES_TRANSIT = [
    # Double paiement client. CAFERMI (#7440) revire 532,03 le 24/08 SANS
    # communication. INV/2026/03522 (532,03) est deja soldee : elle avait ete
    # apuree le 14/07 avec le trop-percu du 21/10/2025 (BNK1/25-26/1622, 752,51
    # verse en double sur INV/2025/03524, comm erronee 000/0023/78419).
    # Solde client actuel -185,48 ; seule piece ouverte : INV/2026/03735 (35,00).
    # -> credit ouvert sur le compte client, sans lettrage (methode acompte/double
    #    paiement). Apres l'operation : 752,51 de credit vs 35,00 du = 717,51 en
    #    faveur de Cafermi, a rembourser ou a imputer sur les prochaines factures.
    {"bsl": 20540, "acc": ACC_400000, "partner": 7440,
     "label": "CAFERMI 532,03 - double paiement, credit ouvert sur le compte client"},

    # Virement interne ING -> Belfius. BE30 3631 6408 2311 = journal 14 (ING),
    # BE86 0689 5807 1350 = journal 36 (Belfius). Le releve ING s'arrete au 24/08 :
    # la contrepartie -15.000,00 n'est pas encore importee. On repointe sur 580000
    # (compte lettrable) : le lettrage se fera a l'import du cote ING.
    {"bsl": 20561, "acc": ACC_580000, "partner": None,
     "label": "Virement interne ING->Belfius 15.000,00 du 26/08 - 580000 (contrepartie a venir)"},
]

CASES_AML = []

# ---------------------------------------------------------------------------
NON_TRAITES = [
    ("ING  20381", "DELHAIZE LE LION       +2.652,97", "avis /ADV/2000058526 toujours non fourni ; subset-sum sur les factures ouvertes = 18 combinaisons <=4 pieces, aucune unique -> exiger l'avis"),
    ("ING  19660 / 20373", "ITM ALIMENTAIRE  +637,24 / +160,61", "ITM Alimentaire Belgium n'existe pas comme partenaire (IBAN BE75 3701 0623 0851) ; paiements de centrale -> exiger l'avis (refs 0000287398 / 0000290027)"),
    ("ING  20522", "AMAZON PAYMENTS           +41,21", "settlement marketplace (SLR4RLYM9OWD9M53), pas le reglement d'une facture client -> rattacher au rapport Amazon"),
    ("ING  19992", "iPiD Europe                +0,01", "micro-depot de verification de compte, pas de piece"),
    ("BELF 19640/19641", "Mollie                 -0,01 x2", "micro-verifications de compte Mollie, pas de piece"),
    ("ING  19625", "KIRCHNER FISCHER    -12.837,54", "domiciliation ; 46 factures ouvertes (161.522,58) : le subset trouve fait 8 pieces, non unique -> exiger l'avis de prelevement"),
    ("BELF 20352", "KIRCHNER clearing   -49.551,11", "meme probleme : le subset trouve fait 14 pieces, non unique -> exiger l'avis de compensation"),
    ("BELF 20350 / 20353", "PRETS ACTIONNAIRES +10.000 / +30.000", "Nira Solutions et Jean-Noel Tilman ; aucun compte courant associe existant (489020 = NOE NATURE, 489030 = TEA TOUCH) -> ARBITRAGE Nicolas : creer 489040/489050 ou utiliser 416100/489100"),
    ("BELF 19188", "PAIEMENT DU PRET      +30.000,00", "mise a disposition du credit Belfius 071-9574936-30 -> ecriture de financement (compte 173/174), pas un lettrage"),
    ("BELF divers", "CHARGES ECHUES CREDIT PROF.", "071-9570627/28/29 et 071-9574936 : mensualites capital+interets, a ventiler sur le tableau d'amortissement -> pas un lettrage"),
    ("BELF divers", "Frais de compte / avis / Business Pack", "3 factures RESA832/894/1047 a 5,14 ne correspondent a aucun prelevement ; les lignes -4,42 / -3,08 / -15,00 / -39,83 n'ont pas de RESA -> charges directes 650000/613xxx"),
    ("ING  19944/20548/20549", "PROXIMUS   -200,00 / -937,17 / -100,00", "14 factures Proximus ouvertes (1.469,94) : aucun montant ni subset ne tombe sur ces prelevements -> factures non encodees ou plan de paiement"),
    ("ING  20546", "WORLDLINE                -541,17", "5 factures ouvertes (2.402,32), aucune a 541,17 -> facture du mois non encodee"),
    ("ING  divers", "Radius / Sendcloud / Google / Skeepers / CILE / Adobe / Intuit / Shopify / Faire / Douanes", "aucune facture d'achat ouverte a ces noms -> charges directes a imputer, rien a lettrer"),
    ("ING  divers", "Virements salaires / avances (van Ooteghem, Cabosart, Vansimpsen)", "avances sur salaire -> 421/453 ou compte courant personnel, pas un lettrage client/fournisseur"),
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
        "ref": f"Write-off ecart reglement lettrage ING+Belfius 26/08 - {label}",
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



def process_draft_bill(case):
    """Valide une facture fournisseur restee en brouillon, puis renvoie son nom."""
    mid, exp, label = case["move_id"], case["expected_total"], case["label"]
    print("=" * 104)
    print(f"[POST BILL] move {mid} -- {label}")
    result = {"bsl_ids": [case.get("bsl")], "label": "POST " + label, "status": None,
              "error": None, "writeoff_move": None, "doc_name": None}
    rows = call("account.move", "read", [[mid]],
                {"fields": ["name", "state", "move_type", "amount_total", "partner_id",
                            "payment_reference", "ref"]})
    if not rows:
        result["status"] = "ERROR"; result["error"] = "move introuvable"
        print("  ERREUR:", result["error"]); return result
    mv = rows[0]
    if mv["move_type"] != "in_invoice":
        result["status"] = "ERROR"; result["error"] = f"move_type={mv['move_type']} != in_invoice"
        print("  ERREUR:", result["error"]); return result
    if (mv.get("partner_id") or [0])[0] != case["partner"]:
        result["status"] = "ERROR"; result["error"] = f"partner {mv.get('partner_id')} != {case['partner']}"
        print("  ERREUR:", result["error"]); return result
    if abs(mv["amount_total"] - exp) > 0.005:
        result["status"] = "ERROR"; result["error"] = f"total {mv['amount_total']:.2f} != {exp:.2f}"
        print("  ERREUR:", result["error"]); return result
    if mv["state"] == "posted":
        print(f"  deja postee : {mv['name']}")
        result["status"] = "SKIP_DEJA_POSTED"; result["doc_name"] = mv["name"]; return result
    if mv["state"] != "draft":
        result["status"] = "ERROR"; result["error"] = f"state={mv['state']}"
        print("  ERREUR:", result["error"]); return result
    print(f"  brouillon OK : {mv['ref']} | {mv['amount_total']:.2f} | comm {mv['payment_reference']}")
    if DRY:
        print("  DRY   action_post()")
        result["status"] = "DRY"; return result
    call("account.move", "action_post", [[mid]])
    after = call("account.move", "read", [[mid]], {"fields": ["name", "state"]})[0]
    print(f"  postee -> {after['name']} (state={after['state']})")
    result["status"] = "OK" if after["state"] == "posted" else "WARN"
    result["doc_name"] = after["name"]
    return result


if __name__ == "__main__":
    print("MODE:", "DRY-RUN (rien ecrit)" if DRY else "APPLY (ecriture reelle)")
    print(f"Tolerance write-off = {ECART_TOLERANCE:.2f} EUR (657100 / 757100)\n")
    results = []

    cases_match = list(CASES_MATCH)
    for c in DRAFT_BILLS_TO_POST:
        r = process_draft_bill(c)
        results.append(r)
        if r["status"] in ("OK", "SKIP_DEJA_POSTED") and r.get("doc_name"):
            cases_match.append({
                "bsl_ids": [c["bsl"]], "acc": ACC_440000, "docs": [r["doc_name"]],
                "label": c["label"],
            })
        elif r["status"] == "DRY":
            print(f"  DRY   -> lettrage BSL {c['bsl']} contre la facture une fois postee\n")

    for c in cases_match:
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
