# -*- coding: utf-8 -*-
"""Scan des lignes ING (BNK1) non lettrees au 10/08/2026 + propositions de matching."""
import os, sys, json, xmlrpc.client
from collections import defaultdict

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

journals = call("account.journal", "search_read", [[["type", "=", "bank"]]],
                {"fields": ["id", "name", "code"]})
print("JOURNAUX BANQUE:", journals)

jids = [j["id"] for j in journals]
bsls = call("account.bank.statement.line", "search_read",
            [[["is_reconciled", "=", False], ["journal_id", "in", jids]]],
            {"fields": ["id", "date", "amount", "partner_id", "payment_ref", "journal_id",
                        "ref", "narration", "move_id"], "order": "date asc, id asc"})
print(f"\nNON LETTREES: {len(bsls)}")
out = []
for b in bsls:
    out.append(b)
    print(f"  [{b['id']}] {b['date']} {b['amount']:>10.2f} | {(b['journal_id'] or ['','?'])[1]:8} | "
          f"{(b['partner_id'] or [0,'-'])[1][:32]:32} | {(b['payment_ref'] or '')[:90]}")

with open(os.path.join(os.path.dirname(__file__), "_scan_ing_20260810.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n-> _scan_ing_20260810.json")
