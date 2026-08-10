# -*- coding: utf-8 -*-
"""Qui a lettre INV/2026/03067, 03056, 03523, 03234 ? (suspicion de lettrage croise)"""
import os, itertools, xmlrpc.client
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = os.environ.get("ODOO_PWD")
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None): return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

for name in ["INV/2026/03067", "INV/2026/03056", "INV/2026/03523", "INV/2026/03234", "INV/2026/01903"]:
    mv = call("account.move", "search_read", [[["name", "=", name]]],
              {"fields": ["id", "partner_id", "amount_total", "amount_residual", "payment_state"]})[0]
    print(f"\n=== {name} (#{mv['id']}) {mv['partner_id'][1]} total={mv['amount_total']} res={mv['amount_residual']} {mv['payment_state']}")
    lines = call("account.move.line", "search_read",
                 [[["move_id", "=", mv["id"]], ["account_id", "=", 162]]],
                 {"fields": ["id", "matched_credit_ids", "matched_debit_ids", "amount_residual", "debit", "credit"]})
    for l in lines:
        print(f"   ligne {l['id']} debit={l['debit']} credit={l['credit']} res={l['amount_residual']}")
        parts = call("account.partial.reconcile", "read", [l["matched_credit_ids"] + l["matched_debit_ids"]],
                     {"fields": ["amount", "debit_move_id", "credit_move_id", "max_date"]})
        for p in parts:
            other = p["credit_move_id"] if p["debit_move_id"][0] == l["id"] else p["debit_move_id"]
            oml = call("account.move.line", "read", [[other[0]]],
                       {"fields": ["move_name", "partner_id", "date", "debit", "credit", "name"]})[0]
            print(f"      <- {p['amount']:>9.2f} le {p['max_date']} par {oml['move_name']} "
                  f"({(oml.get('partner_id') or [0,'-'])[1]}) d={oml['debit']} c={oml['credit']} | {str(oml.get('name'))[:60]}")

# Kirchner : sous-ensemble pour 12837.54
print("\n### KIRCHNER sous-ensembles pour -12837.54 ###")
lines = call("account.move.line", "search_read",
             [[["partner_id", "=", 7195], ["account_id", "=", 192], ["reconciled", "=", False],
               ["parent_state", "=", "posted"], ["amount_residual", "!=", 0]]],
             {"fields": ["move_name", "amount_residual", "date", "id"], "limit": 200, "order": "date"})
vals = [(l, round(l["amount_residual"] * 100)) for l in lines]
sols = []
for n in range(1, 5):
    for c in itertools.combinations(vals, n):
        if abs(sum(x[1] for x in c) + 1283754) <= 1:
            sols.append([x[0]["move_name"] for x in c])
    if len(sols) > 8: break
print(f"  {len(sols)} solution(s):")
for s in sols[:12]: print("   ", s)
