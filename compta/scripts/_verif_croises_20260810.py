# -*- coding: utf-8 -*-
"""Verification lettrages croises : qui est le PAYEUR REEL de BNK1/26-27/0301, /0221, /0495 ?"""
import os, xmlrpc.client
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = os.environ.get("ODOO_PWD")
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None): return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

for name in ["BNK1/26-27/0301", "BNK1/26-27/0221", "BNK1/26-27/0495", "BNK1/26-27/0286"]:
    mv = call("account.move", "search_read", [[["name", "=", name]]],
              {"fields": ["id", "date", "partner_id", "statement_line_id"]})
    if not mv:
        print(name, "introuvable"); continue
    mv = mv[0]
    st = call("account.bank.statement.line", "read", [[mv["statement_line_id"][0]]],
              {"fields": ["date", "amount", "payment_ref", "partner_id"]})[0]
    print(f"\n=== {name} ({mv['date']}) partner du move = {mv['partner_id']}")
    print(f"    PAYEUR REEL : {st['amount']:.2f} :: {st['payment_ref'][:220]}")

print("\n### Factures voisines de meme montant ###")
for nm in ["INV/2026/03057", "INV/2026/03066", "INV/2026/03068", "INV/2026/02701", "INV/2026/02699"]:
    r = call("account.move", "search_read", [[["name", "=", nm]]],
             {"fields": ["name", "partner_id", "amount_total", "amount_residual", "payment_state"]})
    print("  ", r)
