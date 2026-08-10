# -*- coding: utf-8 -*-
"""
LETTRAGE ING 10/08/2026 -- passe complete sur les lignes bancaires non lettrees.

Demande Nicolas : "mettre tout ce que tu peux dans ING, les clients tu sais quoi faire
si les montants sont legerement differents".

Regle d'ecart (validee 26/07 et 29/07/2026) :
  |ecart| <= 5,00 EUR  -> lettrage + write-off 657100 (charge) / 757100 (produit)
  |ecart| >  5,00 EUR  -> lettrage PARTIEL explicite (allow_partial), jamais de write-off

Trois types de traitement :
  A/B  MATCH    : repointage 499000 -> 400000/440000 + reconcile sur la ou les factures
  C/D/E TRANSIT : repointage 499000 -> compte d'imputation etabli (580003 titres-repas,
                  580004 bons Smartbox, 440000 fournisseur) sans lettrage -- precedent
                  historique verifie ligne par ligne dans Odoo
  F    ACOMPTE  : repointage 499000 -> 400000 + partenaire, SANS lettrage : le client a
                  paye deux fois ou paye d'avance, le solde reste visible en credit sur
                  son compte (balance agee) en attendant remboursement/imputation

NOTE CONFIDENTIALITE : repo PUBLIC. Le detail de l'analyse (cas a statuer, anomalies de
lettrages croises) va dans le repo PRIVE Teatower-Direction.

Usage : python lettrage_18_ing_20260810.py            (DRY-RUN)
        python lettrage_18_ing_20260810.py --apply
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
ACC_580003 = 821   # Paiement Sodexo-Edenred (titres-repas)
ACC_580004 = 1225  # Bons cadeaux Smartbox
ACC_657100 = 293   # Negative Payment Differences
ACC_757100 = 347   # Positive Payment Differences
JOURNAL_MISC = 11
TODAY = "2026-08-10"
ECART_TOLERANCE = 5.00

DRY = "--apply" not in sys.argv

# ---------------------------------------------------------------------------
# A/B -- encaissements clients + domiciliation fournisseur avec facture identifiee
# ---------------------------------------------------------------------------
CASES_MATCH = [
    {"bsl_ids": [20197], "acc": ACC_400000, "docs": ["INV/2026/03623"],
     "label": "RAMHORECA SA - INV/2026/03623 793,97 (n de facture dans la communication)"},
    {"bsl_ids": [20207], "acc": ACC_400000, "docs": ["INV/2026/00441"],
     "label": "DJM.BM / Les pieds dans le plat - INV/2026/00441 254,85 (comm structuree 000/0030/06895)"},
    {"bsl_ids": [20212], "acc": ACC_400000, "docs": ["INV/2026/03350"],
     "label": "SA MARER / AD Rochefort - INV/2026/03350 346,87 (comm structuree 000/0041/81407)"},
    {"bsl_ids": [20229], "acc": ACC_400000, "docs": ["INV/2026/03441"],
     "label": "A2MG SRL - INV/2026/03441 73,15 (comm structuree 000/0042/40112)"},
    {"bsl_ids": [20231], "acc": ACC_400000, "docs": ["INV/2026/03736"],
     "label": "LA TABLE DE MANON - INV/2026/03736 74,20 (comm structuree 000/0043/90157)"},
    {"bsl_ids": [20254], "acc": ACC_400000, "docs": ["INV/2026/03447"],
     "label": "NIJSKENS et Cie / Rochefrais - INV/2026/03447 381,60 (comm structuree 000/0042/40718)"},
    {"bsl_ids": [20228], "acc": ACC_400000, "docs": ["INV/2026/03420"],
     "label": "ITM ALIMENTAIRE / Centrale Intermarche - INV/2026/03420 123,10 exact"},
    {"bsl_ids": [20253], "acc": ACC_400000, "docs": ["INV/2026/03632"],
     "label": "MONSIM SA / Intermarche Mons - INV/2026/03632 47,20 exact (IBAN payeur)"},
    {"bsl_ids": [20203], "acc": ACC_400000, "docs": ["INV/2026/03400"],
     "label": "NDB DIFFUSION / Spar Namur - INV/2026/03400 232,75 (ecart -0,01 -> write-off)"},
    {"bsl_ids": [20247], "acc": ACC_440000, "docs": ["RESA1175"],
     "label": "SINAS GmbH - domiciliation SEPA 1.141,33 sur RESA1175 exact"},
    # 0,02 EUR complementaires du client Roodebeek : imputes en partiel sur sa facture ouverte
    {"bsl_ids": [20008], "acc": ACC_400000, "docs": ["INV/2026/03115"], "allow_partial": True,
     "label": "AD DELHAIZE ROODEBEEK - 0,02 residuel impute en partiel sur INV/2026/03115"},
]

# ---------------------------------------------------------------------------
# C/D/E -- repointage vers un compte de transit (precedent historique)
# ---------------------------------------------------------------------------
CASES_TRANSIT = [
    # Titres-repas -> 580003 (precedent : BSL 19334, 19294, 19123, 18984...)
    {"bsl": 19652, "acc": ACC_580003, "partner": None, "label": "PLUXEE 124,95 - titres-repas"},
    {"bsl": 19771, "acc": ACC_580003, "partner": None, "label": "PLUXEE 33,28 - titres-repas"},
    {"bsl": 20052, "acc": ACC_580003, "partner": None, "label": "PLUXEE 6,85 - titres-repas"},
    {"bsl": 20198, "acc": ACC_580003, "partner": None, "label": "PLUXEE 44,98 - titres-repas"},
    {"bsl": 20209, "acc": ACC_580003, "partner": None, "label": "PLUXEE 37,08 - titres-repas"},
    {"bsl": 19826, "acc": ACC_580003, "partner": None, "label": "EDENRED 17,59 - titres-repas"},
    {"bsl": 20050, "acc": ACC_580003, "partner": None, "label": "EDENRED 19,66 - titres-repas"},
    {"bsl": 20210, "acc": ACC_580003, "partner": None, "label": "EDENRED 20,54 - titres-repas"},
    {"bsl": 20211, "acc": ACC_580003, "partner": None, "label": "EDENRED 21,95 - titres-repas"},
    {"bsl": 20141, "acc": ACC_580003, "partner": None, "label": "MONIZZE 19,64 - titres-repas"},
    {"bsl": 20163, "acc": ACC_580003, "partner": None, "label": "MONIZZE 31,25 - titres-repas"},
    {"bsl": 20230, "acc": ACC_580003, "partner": None, "label": "MONIZZE 18,77 - titres-repas"},
    # Bons cadeaux Smartbox -> 580004 (precedent : BSL 18958, 18335, 17923, 17605)
    {"bsl": 19784, "acc": ACC_580004, "partner": None, "label": "SMARTBOX 67,00 - bons cadeaux"},
    {"bsl": 20089, "acc": ACC_580004, "partner": None, "label": "SMARTBOX 40,40 - bons cadeaux"},
    # Assureur -> 440000 Baloise (precedent : BSL 17361, 16600, 15814, 15815)
    {"bsl": 19630, "acc": ACC_440000, "partner": 7382,
     "label": "BALOISE 79,51 - adaptation salaire accident du travail A/26.00112"},
    # F -- acomptes / doubles paiements clients : credit ouvert sur le compte client
    {"bsl": 19466, "acc": ACC_400000, "partner": 2812,
     "label": "NANRETAIL 675,58 - comm 000/0038/68983 = INV/2026/02700 DEJA PAYEE -> credit client"},
    {"bsl": 19952, "acc": ACC_400000, "partner": 113216,
     "label": "DYNAMIC FOOD 436,84 - comm 000/0040/30348 = INV/2026/03067 DEJA PAYEE -> credit client"},
    {"bsl": 20026, "acc": ACC_400000, "partner": 124368,
     "label": "SPAR MOMIGNIES 688,87 - comm 000/0040/27924 = INV/2026/03056 DEJA PAYEE -> credit client"},
    {"bsl": 20065, "acc": ACC_400000, "partner": 2785,
     "label": "BISTRO TOURNESOLS 144,84 - INV/2026/01903 DEJA soldee par les avoirs 2024 -> credit client"},
]


# ---------------------------------------------------------------------------
# Helpers (repris de lettrage_13/15/17)
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
        "ref": f"Write-off ecart reglement lettrage ING 10/08 - {label}",
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


if __name__ == "__main__":
    print("MODE:", "DRY-RUN (rien ecrit)" if DRY else "APPLY (ecriture reelle)")
    print(f"Tolerance write-off = {ECART_TOLERANCE:.2f} EUR (657100 / 757100)\n")
    results = []
    for c in CASES_MATCH:
        results.append(process_match(c))
    for c in CASES_TRANSIT:
        results.append(process_transit(c))

    print("\n" + "=" * 104)
    print("RECAPITULATIF")
    print("=" * 104)
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(f" BSL {str(r['bsl_ids']):>12} | {r['label'][:66]:66} | {str(r['status']):22} "
              f"| wo={r.get('writeoff_move')} | {r.get('error') or ''}")
    print("\n ", counts)
