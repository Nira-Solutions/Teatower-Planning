# -*- coding: utf-8 -*-
import os, sys, xmlrpc.client
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = os.environ["ODOO_PWD"]
UID = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")
def call(mo, me, a, k=None): return _m.execute_kw(DB, UID, PWD, mo, me, a, k or {})

print("--- SumUp PID des precedents ---")
for i in [20569, 20447, 20303, 20162]:
    r = call("account.bank.statement.line", "read", [[i]], {"fields": ["payment_ref"]})[0]
    print(i, (r["payment_ref"] or "").replace("\n", " ")[:120])

print("\n--- comptes 5830xx ---")
print(call("account.account", "search_read", [[["code", "like", "5830"]]],
           {"fields": ["id", "code", "name"]}))

print("\n--- factures clients ouvertes a 637,24 / 160,61 ---")
for amt in (637.24, 160.61, 637.25, 160.60):
    r = call("account.move", "search_read",
             [[["move_type", "=", "out_invoice"], ["state", "=", "posted"],
               ["payment_state", "in", ["not_paid", "partial"]],
               ["amount_total", ">=", amt - 0.02], ["amount_total", "<=", amt + 0.02]]],
             {"fields": ["name", "partner_id", "amount_total", "amount_residual", "invoice_date"]})
    print(" ", amt, "->", [(x["name"], x["partner_id"][1][:30], x["amount_residual"], x["invoice_date"]) for x in r])
