# -*- coding: utf-8 -*-
"""MATCHER lecture seule : propose un rapprochement pour chaque BSL non lettree ING/Belfius."""
import os, re, json
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

JOURNALS = {14: "ING", 36: "BELFIUS"}
rows = call("account.bank.statement.line", "search_read",
            [[["journal_id", "in", list(JOURNALS)], ["is_reconciled", "=", False]]],
            {"fields": ["id", "date", "payment_ref", "amount", "partner_id", "journal_id"],
             "order": "date asc, id asc"})

RE_STRUCT = re.compile(r"(\d{3})/(\d{4})/(\d{5})")
RE_IBAN = re.compile(r"\b(BE\d{14}|[A-Z]{2}\d{2}[A-Z0-9]{10,30})\b")
RE_INV = re.compile(r"\b(INV/\d{4}/\d{4,6}|RINV/\d{2}-\d{2}/\d{4}|RESA\d{3,6})\b", re.I)

def struct_variants(a, b, c):
    return [f"+++{a}/{b}/{c}+++", f"***{a}/{b}/{c}***", f"{a}/{b}/{c}", f"{a}{b}{c}"]

print(f"{len(rows)} lignes a analyser\n")
res = []
for r in rows:
    ref = (r.get("payment_ref") or "").replace("\n", " ")
    j = JOURNALS[r["journal_id"][0]]
    hit = None
    # 1) communication structuree
    ms = RE_STRUCT.search(ref)
    if ms:
        for v in struct_variants(*ms.groups()):
            found = call("account.move", "search_read", [[["payment_reference", "like", v]]],
                         {"fields": ["name", "payment_state", "amount_total", "amount_residual",
                                     "partner_id", "move_type", "state"]})
            if found:
                hit = ("STRUCT " + v, found); break
    # 2) numero de facture en clair
    if not hit:
        mi = RE_INV.search(ref)
        if mi:
            found = call("account.move", "search_read", [[["name", "=ilike", mi.group(1)]]],
                         {"fields": ["name", "payment_state", "amount_total", "amount_residual",
                                     "partner_id", "move_type", "state"]})
            if not found:
                found = call("account.move", "search_read", [[["ref", "ilike", mi.group(1)]]],
                             {"fields": ["name", "payment_state", "amount_total", "amount_residual",
                                         "partner_id", "move_type", "state"]})
            if found:
                hit = ("DOC " + mi.group(1), found)
    # 3) IBAN payeur
    if not hit:
        for ib in RE_IBAN.findall(ref):
            ib = ib.replace(" ", "")
            banks = call("res.partner.bank", "search_read", [[["sanitized_acc_number", "=", ib]]],
                         {"fields": ["partner_id", "acc_number"]})
            if banks:
                pid = banks[0]["partner_id"][0]
                inv = call("account.move", "search_read",
                           [[["partner_id", "child_of", pid], ["state", "=", "posted"],
                             ["payment_state", "in", ["not_paid", "partial"]],
                             ["move_type", "in", ["out_invoice", "out_refund", "in_invoice", "in_refund"]]]],
                           {"fields": ["name", "payment_state", "amount_total", "amount_residual",
                                       "partner_id", "move_type"], "limit": 40})
                hit = (f"IBAN {ib} -> {banks[0]['partner_id'][1]}", inv)
                break
    tag = "---"
    detail = ""
    if hit:
        tag, found = hit
        exact = [f for f in found if abs(abs(f["amount_residual"]) - abs(r["amount"])) < 0.005]
        near = [f for f in found if 0.005 <= abs(abs(f["amount_residual"]) - abs(r["amount"])) <= 5.0]
        pick = exact or near or found[:4]
        detail = " ; ".join(f"{f['name']} res={f['amount_residual']:.2f} tot={f['amount_total']:.2f} {f['payment_state']} [{(f.get('partner_id') or [0,''])[1][:22]}]" for f in pick[:4])
        if exact: tag += " |EXACT|"
        elif near: tag += " |<=5EUR|"
    print(f"{r['id']:>6} {j:<7} {r['date']} {r['amount']:>11,.2f} | {tag[:46]:46} | {detail[:170]}")
    res.append({"id": r["id"], "j": j, "date": r["date"], "amount": r["amount"], "ref": ref,
                "tag": tag, "detail": detail})

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_match_20260826.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
