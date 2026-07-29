# -*- coding: utf-8 -*-
"""
LETTRAGE ING 29/07/2026 -- 49 lignes "a rapprocher" sur BNK1 (ING BE30 3631 6408 2311).

Methode reprise de compta/lettrage_11_ing_20260726.py (validee), etendue a 3 familles :
  A. CLIENTS   -- repointage suspense 499000 -> 400000 + reconcile facture(s).
                  Ecart <= 5,00 EUR : write-off 657100 (client a sous-paye) / 757100 (trop-percu),
                  regle validee par Nicolas (26/07, reconfirmee 29/07 "difference de qlqs euros").
                  Ecart > 5,00 EUR : lettrage PARTIEL sans write-off (allow_partial), jamais a l'aveugle.
  B. FOURNISSEURS -- meme mecanique mais 499000 -> 440000 + reconcile facture(s) fournisseur.
                  Les montants sont negatifs des deux cotes (BSL debit, facture credit).
  C. VIREMENTS INTERNES BNK1 <-> BNK2 -- les 2 lignes de releve miroir sont repointees vers
                  580000 "Internal Transfers of Funds" (id 233, reconcile=True) puis lettrees
                  entre elles. Solde net zero, aucune ecriture de resultat.

CAS PARTICULIER BSL 19806 (Kirchner -2.545,24) :
  Le releve cite explicitement RGK26-02510 (401,64) + RGK26-02511 (2.143,60) = 2.545,24 pile.
  Or RESA747 (RGK26-02511) portait deja un lettrage partiel de 199,41 avec la note de credit
  RBILL/26-27/07/0001 (GSK26-000261). Kirchner a preleve la facture PLEINE : la note de credit
  n'a donc pas ete deduite. Le script delettre cette imputation (remove_move_reconcile) pour
  retomber sur 2.143,60, puis lettre le prelevement. La note de credit 199,41 redevient ouverte
  et sera deduite d'un prelevement futur -- c'est la realite bancaire, confirmee par le libelle.

NON TRAITES (voir compta/review/lettrage_ing_20260729_review.md) : 34 lignes, dont
  - 15 frais/cartes sans facture fournisseur encodee (Google, Adobe, Shopify, Intuit, Sendcloud,
    Worldline, Radius x2, MIAMIO, NCA, frais ING, ING Mastercard...) -> imputation OD, pas lettrage ;
  - 4 encaissements clients sans correspondance fiable (NANRETAIL, Centrale Intermarche,
    Smartbox, Dynamic Food) ;
  - 5 flux hors-clients (Baloise, Pluxee x2, Edenred, iPiD micro-depot) ;
  - Kirchner 19625 (-12.837,54, libelle "Siehe Avis", aucune combinaison trouvee),
    ONSS 19811, Douanes 19746, Proximus 19944, avances salaires x3, fichier SEPA groupe 19735.

Usage : python lettrage_12_ing_20260729.py            (DRY-RUN, rien ecrit)
        python lettrage_12_ing_20260729.py --apply
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
ACC_400000 = 162   # clients
ACC_440000 = 192   # fournisseurs
ACC_580000 = 233   # Internal Transfers of Funds
ACC_657100 = 293   # Negative Payment Differences
ACC_757100 = 347   # Positive Payment Differences
JOURNAL_MISC = 11
TODAY = "2026-07-29"
ECART_TOLERANCE = 5.00

DRY = "--apply" not in sys.argv

# ---------------------------------------------------------------------------
# A + B : encaissements clients et paiements fournisseurs
#   acc          : compte de contrepartie (400000 clients / 440000 fournisseurs)
#   docs         : noms des account.move a solder
#   unreconcile  : moves dont il faut d'abord retirer le lettrage existant
#   allow_partial: ecart > tolerance accepte volontairement (pas de write-off)
# ---------------------------------------------------------------------------
CASES = [
    # --- A. CLIENTS ---------------------------------------------------------
    {"bsl_ids": [19980], "acc": ACC_400000, "docs": ["INV/2026/03139"],
     "label": "SA Barthe - Intermarche Assesse (ecart -0,02)"},
    {"bsl_ids": [19981], "acc": ACC_400000, "docs": ["INV/2026/03210"],
     "label": "Wonka S.A. - Intermarche Heusy (ecart +0,01)"},
    {"bsl_ids": [19914], "acc": ACC_400000, "docs": ["INV/2026/03528", "INV/2026/03512"],
     "label": "Spar Vaux-sur-Sure (680,54 + 39,90 = 720,44 pile)"},
    {"bsl_ids": [19815], "acc": ACC_400000, "docs": ["INV/2026/02758"], "allow_partial": True,
     "label": "Faire.Com - commission Faire 15,65 retenue (lettrage partiel)"},

    # --- B. FOURNISSEURS ----------------------------------------------------
    {"bsl_ids": [19499], "acc": ACC_440000, "docs": ["RESA1152"],
     "label": "SD Worx - facture 8705453 (exact)"},
    {"bsl_ids": [19808], "acc": ACC_440000, "docs": ["RESA1141"],
     "label": "EZCharge/EasyPlug - comm structuree 000/0267/48657 (exact)"},
    {"bsl_ids": [19672], "acc": ACC_440000, "docs": ["RESA1165"],
     "label": "Shyfter SA - facture 2026070568 (exact)"},
    {"bsl_ids": [19675], "acc": ACC_440000,
     "docs": ["RESA853", "RESA852", "RESA847", "RESA854"],
     "label": "Kirchner+Mount Everest - RGK 03222+03268+03333+03223 = 8.129,06 pile"},
    {"bsl_ids": [19806], "acc": ACC_440000, "docs": ["RESA748", "RESA747"],
     "unreconcile": ["RESA747"],
     "label": "Kirchner - RGK 02510+02511 = 2.545,24 (delettrage prealable NC 199,41)"},
    {"bsl_ids": [19477], "acc": ACC_440000, "docs": ["RESA1155"], "allow_partial": True,
     "label": "SD Worx - acompte 110,63 sur facture 8644575 (lettrage partiel)"},
]

# ---------------------------------------------------------------------------
# C : virements internes BNK1 <-> BNK2 (paires de lignes de releve miroir)
# ---------------------------------------------------------------------------
INTERNAL = [
    {"a": 19682, "b": 19664, "amount": 500.00, "label": "10/07 BNK2 -> BNK1 500,00"},
    {"a": 19812, "b": 19756, "amount": 300.00, "label": "16/07 BNK2 -> BNK1 300,00"},
    {"a": 19813, "b": 19757, "amount": 2000.00, "label": "16/07 BNK2 -> BNK1 2.000,00"},
    {"a": 19950, "b": 19917, "amount": 1000.00, "label": "24/07 BNK2 -> BNK1 1.000,00"},
    {"a": 19926, "b": 19890, "amount": 5800.00, "label": "23/07 BNK1 -> BNK2 5.800,00"},
]


# ---------------------------------------------------------------------------
# Helpers
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
        "ref": f"Write-off ecart reglement lettrage ING 29/07 - {label}",
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
# A + B
# ---------------------------------------------------------------------------
def process_case(case):
    bsl_ids = case["bsl_ids"]
    acc = case["acc"]
    docs = case["docs"]
    label = case["label"]
    allow_partial = case.get("allow_partial", False)
    print("=" * 100)
    kind = "CLIENT" if acc == ACC_400000 else "FOURNISSEUR"
    print(f"[{kind}] BSL {bsl_ids} -- {label}")
    result = {"bsl_ids": bsl_ids, "label": label, "status": None, "error": None, "writeoff_move": None}

    # Idempotence : si les lignes de releve sont deja lettrees, ce cas a deja tourne.
    # A tester AVANT de chercher les lignes ouvertes des documents (qui sont alors soldes).
    for bsl_id in bsl_ids:
        pre = get_bsl(bsl_id)
        if pre and pre["is_reconciled"]:
            print(f"  BSL {bsl_id} deja reconciliee -- SKIP (cas deja traite)")
            result["status"] = "SKIP_DEJA_RECONCILED"
            return result

    # --- delettrage prealable eventuel
    for dname in case.get("unreconcile", []):
        d = get_doc(dname)
        if not d:
            result["status"] = "ERROR"; result["error"] = f"Doc {dname} introuvable (unreconcile)"
            print("  ERREUR:", result["error"]); return result
        # remove_move_reconcile() vit sur account.move.line (pas sur account.move) en Odoo 18.
        target = call("account.move.line", "search_read",
                      [[["move_id", "=", d["id"]], ["account_id", "=", acc]]], {"fields": ["id"]})
        if DRY:
            print(f"  DRY   delettrage prealable de {dname} lignes={[t['id'] for t in target]} "
                  f"(residual actuel {d['amount_residual']:.2f})")
        else:
            # remove_move_reconcile() renvoie None -> meme faux echec de marshalling que reconcile()
            try:
                call("account.move.line", "remove_move_reconcile", [[t["id"] for t in target]])
            except xmlrpc.client.Fault as f:
                low = str(f.faultString).lower()
                if "cannot marshal" not in low and "nonetype" not in low:
                    raise
            d2 = get_doc(dname)
            print(f"  UNREC {dname} : residual {d['amount_residual']:.2f} -> {d2['amount_residual']:.2f}")

    # --- partenaire de reference : celui porte par la 1ere ligne ouverte du 1er doc
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

    # --- cote banque : repointer 499000 -> compte de contrepartie
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

    # --- cote documents
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
        # En DRY le delettrage prealable n'a pas eu lieu : on simule le residual d'apres
        # le montant total du document, sinon l'ecart affiche est faux (cas RESA747).
        simulate = DRY and dname in case.get("unreconcile", [])
        for l in lines:
            doc_line_ids.append(l["id"])
            if simulate:
                sign = 1.0 if l["amount_residual"] >= 0 else -1.0
                total_docs += sign * d["amount_total"]
            else:
                total_docs += l["amount_residual"]
        shown = ("%.2f (simule delettrage)" % d["amount_total"]) if simulate else ("%.2f" % d["amount_residual"])
        doc_names.append(dname)
        print(f"    {dname} : residual={shown} lignes={[l['id'] for l in lines]}")

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

    # --- verification finale
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


# ---------------------------------------------------------------------------
# C : virements internes
# ---------------------------------------------------------------------------
def process_internal(pair):
    a, b, label = pair["a"], pair["b"], pair["label"]
    print("=" * 100)
    print(f"[INTERNE] BSL {a} <-> {b} -- {label}")
    result = {"bsl_ids": [a, b], "label": f"VIREMENT INTERNE {label}", "status": None,
              "error": None, "writeoff_move": None}
    lines = []
    total = 0.0
    for bid in (a, b):
        bsl = get_bsl(bid)
        if not bsl:
            result["status"] = "ERROR"; result["error"] = f"BSL {bid} introuvable"
            print("  ERREUR:", result["error"]); return result
        if bsl["is_reconciled"]:
            print(f"  BSL {bid} deja reconciliee -- SKIP"); result["status"] = "SKIP_DEJA_RECONCILED"; return result
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
    print(f"  RESULTAT: {result['status']}")
    return result


if __name__ == "__main__":
    print("MODE:", "DRY-RUN (rien ecrit)" if DRY else "APPLY (ecriture reelle)")
    print(f"Tolerance write-off = {ECART_TOLERANCE:.2f} EUR (657100 / 757100)\n")
    results = []
    for c in CASES:
        results.append(process_case(c))
    for p in INTERNAL:
        results.append(process_internal(p))

    print("\n" + "=" * 100)
    print("RECAPITULATIF")
    print("=" * 100)
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(f" BSL {str(r['bsl_ids']):>16} | {r['label'][:62]:62} | {str(r['status']):22} "
              f"| wo={r.get('writeoff_move')} | {r.get('error') or ''}")
    print("\n ", counts)
