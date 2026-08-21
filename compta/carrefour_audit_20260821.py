# -*- coding: utf-8 -*-
"""AUDIT Carrefour (lecture seule) : que contient reellement la balance agee ?"""
import os
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None): return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

# 1) toutes les fiches Carrefour
parts = call("res.partner", "search_read",
             [["|", ["name", "ilike", "carrefour"], ["name", "ilike", "CRF"]]],
             {"fields": ["id", "name", "parent_id", "vat", "is_company", "customer_rank"],
              "limit": 400})
print(f"=== {len(parts)} fiches 'Carrefour/CRF'")
for p in parts[:60]:
    print(f"  #{p['id']:<7} {p['name'][:56]:<56} parent={p['parent_id']} vat={p['vat']}")

pids = [p["id"] for p in parts]

# 2) lignes 400000 ouvertes sur ces fiches (factures ET paiements/credits)
lines = call("account.move.line", "search_read",
             [[["account_id", "=", 162], ["partner_id", "in", pids], ["reconciled", "=", False],
               ["parent_state", "=", "posted"]]],
             {"fields": ["id", "move_id", "move_name", "date", "debit", "credit",
                         "amount_residual", "partner_id", "journal_id", "name"],
              "order": "date asc"})
deb = [l for l in lines if l["amount_residual"] > 0.005]
cre = [l for l in lines if l["amount_residual"] < -0.005]
print(f"\n=== 400000 ouvert sur Carrefour : {len(lines)} lignes")
print(f"  DEBITS  (factures impayees) : {len(deb):>4}  {sum(l['amount_residual'] for l in deb):>12,.2f}")
print(f"  CREDITS (paiements/avoirs)  : {len(cre):>4}  {sum(l['amount_residual'] for l in cre):>12,.2f}")
print(f"  SOLDE NET                   :        {sum(l['amount_residual'] for l in lines):>12,.2f}")

print("\n--- CREDITS ouverts (a imputer) ---")
for l in cre:
    print(f"  {l['id']:>7} {l['date']} {l['move_name']:<22} {l['amount_residual']:>11,.2f} "
          f"[{l['journal_id'][1][:14]}] {l['partner_id'][1][:26]} | {(l['name'] or '')[:40]}")

print("\n--- DEBITS ouverts par annee ---")
byyear = {}
for l in deb:
    byyear.setdefault(l["date"][:4], [0, 0.0])
    byyear[l["date"][:4]][0] += 1
    byyear[l["date"][:4]][1] += l["amount_residual"]
for y in sorted(byyear):
    print(f"  {y} : {byyear[y][0]:>4} lignes  {byyear[y][1]:>12,.2f}")

# 3) lignes bancaires Carrefour non lettrees (tous journaux bancaires)
bsl = call("account.bank.statement.line", "search_read",
           [[["is_reconciled", "=", False], ["payment_ref", "ilike", "carrefour"]]],
           {"fields": ["id", "date", "amount", "journal_id", "payment_ref"], "order": "date asc"})
print(f"\n=== Lignes bancaires 'CARREFOUR' non lettrees : {len(bsl)}  "
      f"total {sum(b['amount'] for b in bsl):,.2f}")
for b in bsl:
    print(f"  {b['id']:>6} {b['date']} {b['amount']:>11,.2f} [{b['journal_id'][1]}]")
