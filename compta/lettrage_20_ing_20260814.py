# -*- coding: utf-8 -*-
"""
LETTRAGE ING 14/08/2026 -- passe sur les lignes bancaires non lettrees.

Demande Nicolas : "fais le lettrage de ING, tu sais quoi faire pour les factures clients".

Regle d'ecart (validee 26/07 et 29/07/2026, cf feedback_compta_ecart_reglement_tolerance) :
  |ecart| <= 5,00 EUR  -> lettrage + write-off 657100 (charge) / 757100 (produit)
  |ecart| >  5,00 EUR  -> lettrage PARTIEL explicite (allow_partial), jamais de write-off

Quatre types de traitement :
  A MATCH    : repointage 499000 -> 400000 + reconcile sur la facture identifiee par la
               communication structuree BE (cle maitre, cf reference_lettrage_ing_methode)
  B TRANSIT  : repointage 499000 -> compte etabli (580003 titres-repas) sans lettrage
  C ACOMPTE  : repointage 499000 -> 400000 + partenaire SANS lettrage (aucune facture
               ouverte en face : l'argent reste visible en credit sur le compte client)
  D INTERNE  : virement TEATOWER ING <-> TEATOWER Belfius : les 2 lignes miroir sont
               repointees vers 580000 Internal Transfers of Funds puis lettrees entre elles

NON TRAITES VOLONTAIREMENT (voir RECAP en fin d'execution) :
  - BSL 20156 CARREFOUR 4.862,06 : 75 factures ouvertes, aucun sous-ensemble unique,
    communication sans detail (/ADV/) -> exiger l'avis de paiement Carrefour.
  - BSL 19660 ITM ALIMENTAIRE 637,24 : aucune combinaison a +/-5 EUR sur les factures
    ouvertes Centrale Intermarche -> exiger l'avis de paiement.
  - BSL 19992 iPiD Europe 0,01 : micro-depot de verification de compte, pas un reglement
    client (le match "montant exact" sur INV/2026/02482 Belgradis est fortuit).

NOTE CONFIDENTIALITE : repo PUBLIC, pas de secret ici (ODOO_PWD en variable d'env).

Usage : python lettrage_20_ing_20260814.py            (DRY-RUN)
        python lettrage_20_ing_20260814.py --apply
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
ACC_580000 = 233   # Internal Transfers of Funds
ACC_580003 = 821   # Paiement Sodexo-Edenred (titres-repas)
ACC_657100 = 293   # Negative Payment Differences
ACC_757100 = 347   # Positive Payment Differences
JOURNAL_MISC = 11
TODAY = "2026-08-14"
ECART_TOLERANCE = 5.00

DRY = "--apply" not in sys.argv

# ---------------------------------------------------------------------------
# A -- encaissements clients avec facture identifiee (comm. structuree BE)
# ---------------------------------------------------------------------------
CASES_MATCH = [
    {"bsl_ids": [20282], "acc": ACC_400000, "docs": ["INV/2026/03734"],
     "label": "CATHOP SRL - INV/2026/03734 506,20 (comm 000/0043/89955, ecart -0,01)"},
    {"bsl_ids": [20284], "acc": ACC_400000, "docs": ["INV/2026/03514"],
     "label": "CHEZ REMY - INV/2026/03514 153,10 exact (n de facture en clair)"},
    {"bsl_ids": [20331], "acc": ACC_400000, "docs": ["INV/2026/03370"],
     "label": "SA VILLERSEM / Intermarche Villers-le-Bouillet - INV/2026/03370 424,90 (comm 000/0041/88679, ecart -0,01)"},
    {"bsl_ids": [20332], "acc": ACC_400000, "docs": ["INV/2026/03403"],
     "label": "SA MARER / AD Rochefort - INV/2026/03403 266,00 (comm 000/0042/05352, ecart +0,01)"},
]

# ---------------------------------------------------------------------------
# B/C -- repointage sans lettrage
# ---------------------------------------------------------------------------
CASES_TRANSIT = [
    # Titres-repas -> 580003 (precedent : BSL 20141, 20163, 20230, 19334...)
    {"bsl": 20278, "acc": ACC_580003, "partner": None,
     "label": "MONIZZE 19,64 - titres-repas (AMT 20,00 - MSC 0,36)"},
    # Too Good To Go : aucune facture ouverte en face -> credit client
    {"bsl": 20277, "acc": ACC_400000, "partner": 123837,
     "label": "TOO GOOD TO GO BELGIUM 130,07 - aucune facture ouverte -> credit client"},
]

# ---------------------------------------------------------------------------
# D -- virements internes ING <-> Belfius (comptes TEATOWER SA des deux cotes)
# ---------------------------------------------------------------------------
CASES_INTERNAL = [
    {"a": 20149, "b": 20112, "label": "03/08 ING -5.000,00 -> Belfius +5.000,00 (Provision)"},
    {"a": 20184, "b": 20127, "label": "04/08 ING -14.000,00 -> Belfius +14.000,00"},
]


# ---------------------------------------------------------------------------
# Helpers (repris de lettrage_12/18)
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
        "ref": f"Write-off ecart reglement lettrage ING 14/08 - {label}",
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


if __name__ == "__main__":
    print("MODE:", "DRY-RUN (rien ecrit)" if DRY else "APPLY (ecriture reelle)")
    print(f"Tolerance write-off = {ECART_TOLERANCE:.2f} EUR (657100 / 757100)\n")
    results = []
    for c in CASES_MATCH:
        results.append(process_match(c))
    for c in CASES_TRANSIT:
        results.append(process_transit(c))
    for c in CASES_INTERNAL:
        results.append(process_internal(c))

    print("\n" + "=" * 104)
    print("RECAPITULATIF")
    print("=" * 104)
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(f" BSL {str(r['bsl_ids']):>14} | {r['label'][:64]:64} | {str(r['status']):22} "
              f"| wo={r.get('writeoff_move')} | {r.get('error') or ''}")
    print("\n ", counts)
    print("\n NON TRAITES (avis de paiement / piece manquante) :")
    print("  BSL 20156 CARREFOUR BELGIUM  4.862,06 -- 75 factures ouvertes, aucun sous-ensemble unique")
    print("  BSL 19660 ITM ALIMENTAIRE      637,24 -- aucune combinaison a +/-5 EUR chez Centrale Intermarche")
    print("  BSL 19992 iPiD Europe            0,01 -- micro-depot de verification, pas un reglement")
