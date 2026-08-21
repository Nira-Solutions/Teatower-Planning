# -*- coding: utf-8 -*-
"""AUDIT Carrefour v2 : anciennete reelle + facture/encaisse sur 12 mois (lecture seule)."""
import os
from collections import defaultdict
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None): return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

CRF = 6596  # Carrefour Belgium (integre)
TODAY = "2026-08-21"

# --- 1) factures ouvertes du groupe integre, par mois
inv = call("account.move", "search_read",
           [[["partner_id", "child_of", CRF], ["state", "=", "posted"],
             ["payment_state", "in", ["not_paid", "partial"]],
             ["move_type", "in", ["out_invoice", "out_refund"]]]],
           {"fields": ["name", "invoice_date", "invoice_date_due", "amount_total",
                       "amount_residual", "partner_id", "payment_state"],
            "order": "invoice_date asc"})
bym = defaultdict(lambda: [0, 0.0])
for i in inv:
    k = (i["invoice_date"] or "?")[:7]
    bym[k][0] += 1
    bym[k][1] += i["amount_residual"]
print(f"=== Carrefour Belgium (#{CRF} + enfants) : {len(inv)} pieces ouvertes, "
      f"{sum(i['amount_residual'] for i in inv):,.2f} EUR")
print("\n  mois      nb      residuel   cumul")
cum = 0.0
for k in sorted(bym):
    cum += bym[k][1]
    print(f"  {k}  {bym[k][0]:>4}  {bym[k][1]:>12,.2f}  {cum:>12,.2f}")

print("\n--- detail des pieces anterieures a 2026-06 (les vrais 'vieux') ---")
for i in inv:
    if (i["invoice_date"] or "9") < "2026-06-01":
        print(f"  {i['name']:<20} {i['invoice_date']} ech={i['invoice_date_due']} "
              f"res={i['amount_residual']:>10,.2f} tot={i['amount_total']:>10,.2f} "
              f"{i['payment_state']:<9} {i['partner_id'][1][:40]}")

# --- 2) facture vs encaisse sur 12 mois
allm = call("account.move.line", "search_read",
            [[["account_id", "=", 162], ["partner_id", "child_of", CRF],
              ["parent_state", "=", "posted"], ["date", ">=", "2025-09-01"]]],
            {"fields": ["date", "debit", "credit", "journal_id", "move_name"]})
fact = sum(l["debit"] for l in allm)
enc = sum(l["credit"] for l in allm)
print(f"\n=== Mouvements 400000 Carrefour depuis 2025-09-01")
print(f"  DEBITS  (factures)     : {fact:>12,.2f}")
print(f"  CREDITS (paiements/AV) : {enc:>12,.2f}")
print(f"  SOLDE                  : {fact - enc:>12,.2f}")

byj = defaultdict(float)
for l in allm:
    if l["credit"]:
        byj[l["journal_id"][1]] += l["credit"]
print("  credits par journal :", {k: round(v, 2) for k, v in byj.items()})

# --- 3) rythme des encaissements Carrefour (lignes bancaires deja lettrees)
bsl = call("account.bank.statement.line", "search_read",
           [[["payment_ref", "ilike", "carrefour belgium"], ["date", ">=", "2025-09-01"]]],
           {"fields": ["id", "date", "amount", "is_reconciled"], "order": "date asc"})
print(f"\n=== Virements 'CARREFOUR BELGIUM' recus depuis 09/2025 : {len(bsl)}")
for b in bsl:
    print(f"  {b['id']:>6} {b['date']} {b['amount']:>11,.2f} lettree={b['is_reconciled']}")
print(f"  TOTAL recu : {sum(b['amount'] for b in bsl):,.2f}")
