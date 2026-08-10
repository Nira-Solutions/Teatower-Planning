# -*- coding: utf-8 -*-
"""Recherche GLOBALE des communications structurees restantes + compte 580003/580004."""
import os, re, json, xmlrpc.client
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = os.environ.get("ODOO_PWD")
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None): return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

for code in ["580003", "580004", "499000", "757100", "657100"]:
    a = call("account.account", "search_read", [[["code", "=", code]]],
             {"fields": ["id", "code", "name", "reconcile", "account_type"]})
    print(code, a)

bsls = json.load(open(os.path.join(os.path.dirname(__file__), "_scan_ing_20260810.json"), encoding="utf-8"))
print("\n### COMMUNICATIONS STRUCTUREES -> recherche globale ###")
for b in bsls:
    ref = b.get("payment_ref") or ""
    for s in set(re.findall(r"[*+]{3}(\d{3}/\d{4}/\d{5})[*+]{3}", ref)):
        res = call("account.move", "search_read", [[["payment_reference", "like", s]]],
                   {"fields": ["name", "partner_id", "amount_total", "amount_residual",
                               "payment_state", "invoice_date"], "limit": 5})
        print(f"[{b['id']}] {b['date']} {b['amount']:>9.2f} comm {s} ->")
        for r in res:
            print(f"      {r['name']} {r['partner_id'][1][:40]} total={r['amount_total']} "
                  f"res={r['amount_residual']} {r['payment_state']} {r['invoice_date']}")
        if not res:
            print("      (aucune facture avec cette communication)")
