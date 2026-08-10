# -*- coding: utf-8 -*-
"""Investigation ciblee #2 : cas restants ING (10/08/2026)."""
import os, re, json, itertools, xmlrpc.client
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = os.environ.get("ODOO_PWD")
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None): return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

def encours(needle, acc=162, limit=60):
    ps = call("res.partner", "search_read", [[["name", "ilike", needle]]], {"fields": ["id", "name"], "limit": 30})
    out = []
    for p in ps:
        lines = call("account.move.line", "search_read",
                     [[["partner_id", "=", p["id"]], ["account_id", "=", acc], ["reconciled", "=", False],
                       ["parent_state", "=", "posted"], ["amount_residual", "!=", 0]]],
                     {"fields": ["move_name", "amount_residual", "date", "id"], "limit": limit, "order": "date"})
        if lines:
            print(f"  #{p['id']} {p['name']}")
            for l in lines:
                print(f"     {l['move_name']:22} {l['date']} res={l['amount_residual']:>10.2f} line={l['id']}")
            out += [(p, l) for l in lines]
    if not out:
        print(f"  (aucun encours ouvert acc={acc} pour '{needle}')")
    return out

for n, acc in [("Dynamic Food", 162), ("Momignies", 162), ("Roodebeek", 162),
               ("NANRETAIL", 162), ("Centrale Intermarch", 162), ("Tournesols", 162),
               ("Kirchner", 192)]:
    print(f"\n### {n} (acc {acc}) ###")
    encours(n, acc)

print("\n### INV/2026/01903 (Tournesols) ###")
print(call("account.move", "search_read", [[["name", "=", "INV/2026/01903"]]],
           {"fields": ["name", "partner_id", "amount_total", "amount_residual", "payment_state", "invoice_date"]}))

print("\n### Nanretail : factures recentes (toutes) ###")
mv = call("account.move", "search_read",
          [[["partner_id", "child_of", 2812], ["move_type", "in", ["out_invoice", "out_refund"]],
            ["state", "=", "posted"]]],
          {"fields": ["name", "invoice_date", "amount_total", "amount_residual", "payment_state"],
           "order": "invoice_date desc", "limit": 15})
for x in mv: print("  ", x["name"], x["invoice_date"], x["amount_total"], "res=", x["amount_residual"], x["payment_state"])

# --- Carrefour : recherche de sous-ensemble exact pour 4862.06 ---
print("\n### CARREFOUR : sous-ensembles exacts pour 4862.06 ###")
cf = call("res.partner", "search_read", [[["name", "ilike", "carrefour"]]], {"fields": ["id"], "limit": 40})
lines = call("account.move.line", "search_read",
             [[["partner_id", "in", [p["id"] for p in cf]], ["account_id", "=", 162],
               ["reconciled", "=", False], ["parent_state", "=", "posted"], ["amount_residual", "!=", 0]]],
             {"fields": ["move_name", "amount_residual", "date", "id"], "limit": 200, "order": "date"})
target = 486206
sols = []
vals = [(l, round(l["amount_residual"] * 100)) for l in lines]
for n in range(1, 5):
    for combo in itertools.combinations(vals, n):
        if abs(sum(c[1] for c in combo) - target) <= 1:
            sols.append([c[0]["move_name"] for c in combo])
    if len(sols) > 12: break
print(f"  {len(sols)} solution(s) <=4 factures :")
for s in sols[:15]: print("   ", s)
