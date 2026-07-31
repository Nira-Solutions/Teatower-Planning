# -*- coding: utf-8 -*-
"""
LETTRAGE ING 31/07/2026 (2e passe) -- elargissement demande par Nicolas : "lettre TOUT ce qui
est lettrable dans ING", pas seulement les encaissements clients. Complete
compta/lettrage_13_ing_20260731.py (2 encaissements clients) avec les debits fournisseurs et
autres flux ayant une contrepartie DEJA OUVERTE en compta.

REGLE DURE AJOUTEE CE TOUR (Nicolas) : aucune ecriture n'est creee pour une ligne SANS
contrepartie ouverte -- imputer un frais sans facture reviendrait a creer une charge (impact
P&L), interdit sans validation explicite. Ce script ne LETTRE donc QUE contre une
account.move.line deja postee et ouverte (facture fournisseur non soldee). Toutes les lignes
sans contrepartie ouverte sont documentees a part (voir
compta/review/lettrage_ing_20260731_fournisseurs_review.md), avec le compte suggere le cas
echeant, SANS RIEN CREER.

CAS TRAITES (3), tous des matches exacts (ecart 0,00, aucun write-off necessaire) :
  A. BSL 20044 Kirchner, Fischer + Co GmbH (-12.087,45) -- le libelle SEPA cite explicitement
     "R RGK 26-02871, 11.735,45 R RGK26-03856, 352,00" = 12.087,45 pile. RESA792 (RGK26-02871,
     11.735,45, open) + RESA912 (RGK26-03856, 352,00, open).
  B. BSL 20042 Sinas Gmbh & Co (-957,00) -- RESA1117 (ref 201944, 957,00, open) : montant exact,
     aucune ambiguite (Sinas n'a que 3 factures ouvertes, une seule a exactement ce montant).
  C. BSL 20027 ING Belgique SA (-7,26) -- le releve cite explicitement "FACTURE n° 2026/01/005568163
     du 28/07/2026" = RESA1218 (ref 2026/01/005568163, 7,26, open) pile.

Debits/credits documentes mais NON lettres (voir le fichier de revue pour le detail complet et
le raisonnement) :
  - 2 cas "duplicate SDD" Radius (19871 -308,80, 19985 -459,81) : les factures reference dans
    le libelle bancaire (RESA1201, RESA1195) sont deja soldees, mais via des VIEUX prelevements
    de mars 2026 dont le residuel avait ete reparti sur plusieurs factures (mecanisme "pool" a
    l'ancienne). Consequence : ces 2 nouveaux debits n'ont plus de facture ouverte en face --
    aucune contrepartie ouverte, donc rien a lettrer ici (cf. regle dure). Signale pour audit
    Radius separe.
  - 1 cas ecart trop important : BSL 19809 Worldline (-529,78) reference "2260310704" = RESA1059
    (626,31 ouverte), mais ecart de 96,53 EUR (> tolerance 5 EUR) -- pas de lettrage partiel
    force sans confirmation, signale a part.
  - BSL 19625 Kirchner (-12.837,54, "Siehe Avis vom 07.07.26") : AUCUNE reference facture dans le
    libelle. Une recherche exhaustive (subset-sum) sur les 47 factures Kirchner ouvertes trouve
    des dizaines de combinaisons qui tombent pile au centime pres -- avec 47 candidats c'est
    statistiquement inevitable et donc AUCUNE de ces combinaisons ne constitue une preuve
    fiable. Necessite l'avis Kirchner du 07/07 (deja signale le 29/07, toujours vrai).
  - BSL 19811 ONSS (-8.945,00) : le compte 454000 (NSSO) existe mais TOUTES ses lignes non
    reconciliees ont un residuel de 0,00 -- aucun montant ouvert a matcher. Necessite un audit
    ONSS/SD Worx dedie (cf. doublons deja identifies par le passe), hors perimetre bancaire.
  - BSL 19735 (-1.574,53, fichier de virements SEPA groupe) : beneficiaire non identifiable a
    partir du seul libelle de synthese, necessite le detail du fichier.
  - BSL 19746 Douanes et Accises (-1.040,40) et 19944 Proximus (-200,00) : aucune facture
    fournisseur ouverte encodee pour ces beneficiaires -- sans contrepartie, pas de lettrage.
  - BSL 20049 CHEQUE GUICHET (-396,00) : aucune information sur le beneficiaire.
  - BSL 19972/19703/19480 Google Ads, 19788 Shopify, 19728/19638 Adobe, 19639 Intuit,
    19607 Google Cloud, 19804 Mastercard ING (reglement carte, pas une facture), 19853 MIAMIO
    Faire, 19857 NCA Europe Faire, 19460 ING (frais, pas de facture encodee) : AUCUNE facture
    fournisseur ouverte en face (paiements carte historiquement non factures dans Odoo) --
    imputer directement creerait une charge, INTERDIT sans validation. Comptes suggeres dans le
    fichier de revue, rien cree.
  - Avances salariales 19610/19739 (Vansimpsen), 19738 (Cabosart), 19737 (van Ooteghem) :
    historiquement codees directement 455000 Remuneration SANS ligne ouverte prealable a
    matcher (chaque avance passee est auto-soldee dans son propre mouvement) -- pas de
    "contrepartie ouverte" au sens strict de la regle, donc pas de lettrage ; compte suggere
    455000 si Nicolas valide le meme traitement que d'habitude.
  - MIAMIO/NCA Europe (achats Faire par carte) : ATTENTION, l'historique montre que ces
    paiements ont deja ete codes A TORT sur 440000 Suppliers par le passe (ex. RESA visibles
    08/05, 31/03, 23/02, 14/12, 02/12 -- toutes en 440000). Le compte correct constate sur les
    AUTRES achats Faire (Sass Belle, Matcha Passion, YOKO DESIGN, Der kleine Fratz, Ogo living)
    est 600000 Purchases of Raw Materials. Ne PAS reproduire l'erreur 440000 si ces lignes sont
    imputees un jour -- ce script ne les impute de toute facon pas (regle dure).

Usage : python lettrage_14_ing_20260731_fournisseurs.py            (DRY-RUN, rien ecrit)
        python lettrage_14_ing_20260731_fournisseurs.py --apply
"""
import os
import sys
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")  # repo public -- jamais de mot de passe en clair
if not PWD:
    raise SystemExit("Definir ODOO_PWD avant d'executer (creds dans Materiel TT.xlsx).")

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m_obj = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return m_obj.execute_kw(DB, uid, PWD, model, method, args, kw or {})


ACC_499000 = 221   # suspense bancaire
ACC_440000 = 192   # fournisseurs
ACC_657100 = 293   # Negative Payment Differences
ACC_757100 = 347   # Positive Payment Differences
JOURNAL_MISC = 11
TODAY = "2026-07-31"
ECART_TOLERANCE = 5.00

DRY = "--apply" not in sys.argv

CASES = [
    {"bsl_ids": [20044], "acc": ACC_440000, "docs": ["RESA792", "RESA912"],
     "label": "Kirchner - RGK26-02871 (11.735,45) + RGK26-03856 (352,00) = 12.087,45 pile, refs citees dans le libelle"},
    {"bsl_ids": [20042], "acc": ACC_440000, "docs": ["RESA1117"],
     "label": "Sinas Gmbh & Co - facture 201944 (957,00 pile)"},
    {"bsl_ids": [20027], "acc": ACC_440000, "docs": ["RESA1218"],
     "label": "ING Belgique SA - facture 2026/01/005568163 citee dans le libelle (7,26 pile)"},
]


# ---------------------------------------------------------------------------
# Helpers (repris a l'identique de lettrage_12/13)
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
    """reconcile() renvoie parfois None -> Fault de marshalling XML-RPC alors que le lettrage a eu lieu."""
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
        "ref": f"Write-off ecart reglement lettrage ING 31/07 (fournisseurs) - {label}",
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


def process_case(case):
    bsl_ids = case["bsl_ids"]
    acc = case["acc"]
    docs = case["docs"]
    label = case["label"]
    allow_partial = case.get("allow_partial", False)
    print("=" * 100)
    print(f"[FOURNISSEUR] BSL {bsl_ids} -- {label}")
    result = {"bsl_ids": bsl_ids, "label": label, "status": None, "error": None, "writeoff_move": None}

    for bsl_id in bsl_ids:
        pre = get_bsl(bsl_id)
        if pre and pre["is_reconciled"]:
            print(f"  BSL {bsl_id} deja reconciliee -- SKIP (cas deja traite)")
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

    bsl_aml_ids = []
    total_bsl = 0.0
    for bsl_id in bsl_ids:
        bsl = get_bsl(bsl_id)
        if not bsl:
            result["status"] = "ERROR"; result["error"] = f"BSL {bsl_id} introuvable"
            print("  ERREUR:", result["error"]); return result
        if bsl["is_reconciled"]:
            print(f"  BSL {bsl_id} deja reconciliee -- SKIP"); result["status"] = "SKIP_DEJA_RECONCILED"; return result
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

    doc_line_ids = []
    total_docs = 0.0
    doc_names = []
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
            doc_line_ids.append(l["id"])
            total_docs += l["amount_residual"]
        doc_names.append(dname)
        print(f"    {dname} : residual={d['amount_residual']:.2f} lignes={[l['id'] for l in lines]}")

    ecart = round(total_bsl - total_docs, 2)
    print(f"  BSL total={total_bsl:.2f} | docs total (signe)={total_docs:.2f} | ECART={ecart:+.2f}")

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
        result["status"] = "WARN"
        result["error"] = "BSL non reconciliee ou doc non solde"
        print("  RESULTAT: WARN --", result["error"])
    return result


if __name__ == "__main__":
    print("MODE:", "DRY-RUN (rien ecrit)" if DRY else "APPLY (ecriture reelle)")
    print(f"Tolerance write-off = {ECART_TOLERANCE:.2f} EUR (657100 / 757100)\n")
    results = []
    for c in CASES:
        results.append(process_case(c))

    print("\n" + "=" * 100)
    print("RECAPITULATIF")
    print("=" * 100)
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(f" BSL {str(r['bsl_ids']):>16} | {r['label'][:62]:62} | {str(r['status']):22} "
              f"| wo={r.get('writeoff_move')} | {r.get('error') or ''}")
    print("\n ", counts)
