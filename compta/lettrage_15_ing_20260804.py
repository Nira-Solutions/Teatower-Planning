# -*- coding: utf-8 -*-
"""
LETTRAGE ING 04/08/2026 -- reprise complete des 58 lignes ING (BNK1) non reconciliees a date,
demande Nicolas "lettrer TOUT ce qui est lettrable" (clients + fournisseurs + autres).

Methode identique a lettrage_13/14 (repointage suspense 499000 -> compte cible + reconcile).
Ecart <= 5,00 EUR : write-off 657100 (charge, client sous-paye / on a trop verse au fournisseur)
ou 757100 (produit, trop-percu client / on a moins paye le fournisseur que du). Ecart > 5,00 EUR :
jamais de lettrage force.

CAS TRAITES (9), tous des matches exacts ou quasi-exacts (ecart <= 0,02 EUR) :
  CLIENTS (7) :
  A. BSL 20062 (+199,00) Virelles Nature -> INV/2026/02150 (199,00 pile)
  B. BSL 20077 (+256,41) Virelles Nature -> INV/2025/02201 (256,41 pile)
  C. BSL 20066 (+366,11) Hello Bio sprl (Pure Bastogne) -> INV/2026/03314 (366,11 pile)
  D. BSL 20078 (+684,26) Chili Peppers - Intermarche Tilff -> INV/2026/03435 (684,27, ecart -0,01)
  E. BSL 20090 (+697,20) SA LD Management - Intermarche Hamoir -> INV/2026/02836 (697,21, ecart -0,01)
  F. BSL 20102 (+344,45) FQMS - Proxy Delhaize Quadrilatere Huy -> INV/2026/03625 (344,45 pile)
  G. BSL 20070 (+675,02) Centrale Intermarche -> INV/2026/03297 (675,00, ecart +0,02)

  FOURNISSEUR (2), ING Belgique SA (releves de compte cartes, refs facture citees dans le libelle) :
  H. BSL 20080 (-7,26) -> facture fournisseur id 43737, ref 2026/01/005574341 (7,26 pile)
  I. BSL 20103 (-35,45) -> facture fournisseur id 43792, ref 2026/01/005699467 (35,45 pile)

NON TRAITES -- voir compta/review/lettrage_ing_20260804_review.md pour le detail complet.

Usage : python lettrage_15_ing_20260804.py            (DRY-RUN, rien ecrit)
        python lettrage_15_ing_20260804.py --apply
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
ACC_657100 = 293   # Negative Payment Differences
ACC_757100 = 347   # Positive Payment Differences
JOURNAL_MISC = 11
TODAY = "2026-08-04"
ECART_TOLERANCE = 5.00

DRY = "--apply" not in sys.argv

CASES = [
    {"bsl_ids": [20062], "acc": ACC_400000, "docs": ["INV/2026/02150"],
     "label": "Virelles Nature - INV/2026/02150 (199,00 pile)"},
    {"bsl_ids": [20077], "acc": ACC_400000, "docs": ["INV/2025/02201"],
     "label": "Virelles Nature - INV/2025/02201 (256,41 pile)"},
    {"bsl_ids": [20066], "acc": ACC_400000, "docs": ["INV/2026/03314"],
     "label": "Hello Bio sprl (Pure Bastogne) - INV/2026/03314 (366,11 pile)"},
    {"bsl_ids": [20078], "acc": ACC_400000, "docs": ["INV/2026/03435"],
     "label": "Chili Peppers - Intermarche Tilff - INV/2026/03435 (684,27 vs 684,26, ecart -0,01)"},
    {"bsl_ids": [20090], "acc": ACC_400000, "docs": ["INV/2026/02836"],
     "label": "SA LD Management - Intermarche Hamoir - INV/2026/02836 (697,21 vs 697,20, ecart -0,01)"},
    {"bsl_ids": [20102], "acc": ACC_400000, "docs": ["INV/2026/03625"],
     "label": "FQMS - Proxy Delhaize Quadrilatere Huy - INV/2026/03625 (344,45 pile)"},
    {"bsl_ids": [20070], "acc": ACC_400000, "docs": ["INV/2026/03297"],
     "label": "Centrale Intermarche - INV/2026/03297 (675,00 vs 675,02, ecart +0,02)"},
    {"bsl_ids": [20080], "acc": ACC_440000, "doc_ids": [43737],
     "label": "ING Belgique SA - facture 2026/01/005574341 citee dans le libelle (7,26 pile)"},
    {"bsl_ids": [20103], "acc": ACC_440000, "doc_ids": [43792],
     "label": "ING Belgique SA - facture 2026/01/005699467 citee dans le libelle (35,45 pile)"},
]


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


def get_doc(name=None, doc_id=None):
    domain = [["id", "=", doc_id]] if doc_id else [["name", "=", name]]
    rows = call("account.move", "search_read", [domain],
                {"fields": ["id", "name", "ref", "payment_state", "amount_residual", "amount_total",
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
        "ref": f"Write-off ecart reglement lettrage ING 04/08 - {label}",
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
    docs = case.get("docs")
    doc_ids = case.get("doc_ids")
    label = case["label"]
    allow_partial = case.get("allow_partial", False)
    print("=" * 100)
    print(f"BSL {bsl_ids} -- {label}")
    result = {"bsl_ids": bsl_ids, "label": label, "status": None, "error": None, "writeoff_move": None}

    for bsl_id in bsl_ids:
        pre = get_bsl(bsl_id)
        if pre and pre["is_reconciled"]:
            print(f"  BSL {bsl_id} deja reconciliee -- SKIP (cas deja traite)")
            result["status"] = "SKIP_DEJA_RECONCILED"
            return result

    doc_refs = docs if docs else [None] * len(doc_ids)
    id_refs = doc_ids if doc_ids else [None] * len(docs)
    ref_doc = get_doc(name=doc_refs[0], doc_id=id_refs[0])
    if not ref_doc:
        result["status"] = "ERROR"; result["error"] = f"Doc {doc_refs[0] or id_refs[0]} introuvable"
        print("  ERREUR:", result["error"]); return result
    ref_lines = open_lines_on(ref_doc["id"], acc)
    if not ref_lines:
        result["status"] = "ERROR"; result["error"] = f"Aucune ligne {acc} ouverte sur {ref_doc['name']}"
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
    for dname, did in zip(doc_refs, id_refs):
        d = get_doc(name=dname, doc_id=did)
        if not d:
            result["status"] = "ERROR"; result["error"] = f"Doc {dname or did} introuvable"
            print("  ERREUR:", result["error"]); return result
        if d["payment_state"] == "paid":
            print(f"    {d['name']} deja paid -- SKIP"); continue
        lines = open_lines_on(d["id"], acc)
        if not lines:
            result["status"] = "ERROR"; result["error"] = f"Pas de ligne {acc} ouverte pour {d['name']}"
            print("  ERREUR:", result["error"]); return result
        for l in lines:
            doc_line_ids.append(l["id"])
            total_docs += l["amount_residual"]
        doc_names.append(d["name"] or f"id{d['id']}(ref={d.get('ref')})")
        print(f"    {d['name']}(ref={d.get('ref')}) : residual={d['amount_residual']:.2f} lignes={[l['id'] for l in lines]}")

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
    for dname, did in zip(doc_refs, id_refs):
        dc = get_doc(name=dname, doc_id=did)
        print(f"   {dc['name']} payment_state={dc['payment_state']} residual={dc['amount_residual']:.2f}")
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
