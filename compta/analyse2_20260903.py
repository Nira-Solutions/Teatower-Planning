# -*- coding: utf-8 -*-
"""Analyse 2 : precedents SumUp / Get your mug, comm Delembourg, comptes, ITM."""
import os, re, sys
import xmlrpc.client
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = os.environ["ODOO_PWD"]
_c = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common")
UID = _c.authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return _m.execute_kw(DB, UID, PWD, model, method, args, kw or {})

def precedents(pat, n=4):
    print("\n--- precedents '%s' ---" % pat)
    ps = call("account.bank.statement.line", "search_read",
              [[["journal_id", "in", [14, 36]], ["is_reconciled", "=", True],
                ["payment_ref", "ilike", pat]]],
              {"fields": ["id", "date", "amount"], "limit": n, "order": "date desc"})
    for p in ps:
        ml = call("account.move.line", "search_read",
                  [[["move_id.statement_line_id", "=", p["id"]]]],
                  {"fields": ["account_id", "partner_id", "balance"]})
        print("  BSL %d %s %+.2f -> %s" % (p["id"], p["date"], p["amount"],
              [(x["account_id"][1], (x.get("partner_id") or [0, "-"])[1], x["balance"]) for x in ml]))

precedents("SumUp")
precedents("Get your mug")

print("\n--- comm Delembourg 000/0044/01372 ---")
print(call("account.move", "search_read", [[["payment_reference", "like", "000/0044/01372"]]],
           {"fields": ["name", "partner_id", "amount_total", "amount_residual",
                       "payment_state", "state", "invoice_date"]}))

print("\n--- comptes utiles ---")
for code in ["580000", "580003", "580004", "440000", "650000", "552", "550001"]:
    print(code, call("account.account", "search_read", [[["code", "=", code]]],
                     {"fields": ["id", "code", "name", "reconcile"]}))

print("\n--- partner ING Belgique ---")
print(call("res.partner", "search_read", [[["name", "ilike", "ING Belgique"]]],
           {"fields": ["id", "name"], "limit": 5}))

print("\n=== ITM / Centrale Intermarche : grand livre 400000 ===")
p = call("res.partner", "search_read", [[["name", "ilike", "Intermarch"]]],
         {"fields": ["id", "name"], "limit": 20})
print(p)
CENT = [x["id"] for x in p if "entrale" in x["name"]]
if CENT:
    ls = call("account.move.line", "search_read",
              [[["partner_id", "in", CENT],
                ["account_id.account_type", "=", "asset_receivable"],
                ["parent_state", "=", "posted"]]],
              {"fields": ["id", "date", "move_id", "name", "balance", "amount_residual",
                          "reconciled"], "order": "date asc", "limit": 200})
    for l in ls:
        print("  %s %-22s bal=%9.2f res=%9.2f rec=%s" % (
            l["date"], l["move_id"][1][:22], l["balance"], l["amount_residual"], l["reconciled"]))
