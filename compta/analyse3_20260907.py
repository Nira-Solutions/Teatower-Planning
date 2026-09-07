# -*- coding: utf-8 -*-
"""Analyse 3 : SumUp PID, salaires, SD Worx 591,86, Bancontact, Sendcloud/Faire partners."""
import os, sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
UID = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return _m.execute_kw(DB, UID, PWD, model, method, args, kw or {})

print("=== SumUp : libelles complets des precedents (PID) ===")
for r in call("account.bank.statement.line", "search_read",
              [[["journal_id", "in", [14, 36]], ["payment_ref", "ilike", "SumUp"]]],
              {"fields": ["id", "date", "amount", "payment_ref", "is_reconciled", "move_id"],
               "order": "date desc", "limit": 14}):
    print("  %d %s %+9.2f rec=%-5s | %s" % (r["id"], r["date"], r["amount"],
                                            r["is_reconciled"], r["payment_ref"][:150]))

print("\n=== Precedents SALAIRES (Belfius, gros debits) ===")
for pat in ["SALAIRES", "REMUNERATION", "TRAITEMENT"]:
    for r in call("account.bank.statement.line", "search_read",
                  [[["journal_id", "in", [14, 36]], ["payment_ref", "ilike", pat],
                    ["is_reconciled", "=", True]]],
                  {"fields": ["id", "date", "amount", "move_id", "payment_ref"],
                   "order": "date desc", "limit": 5}):
        ls = call("account.move.line", "search_read", [[["move_id", "=", r["move_id"][0]]]],
                  {"fields": ["account_id", "partner_id", "balance"]})
        for l in ls:
            if not l["account_id"][1].startswith("55"):
                print("  [%s] %d %s %+10.2f -> %s | %s" % (
                    pat, r["id"], r["date"], r["amount"], l["account_id"][1][:40],
                    (l.get("partner_id") or [0, "-"])[1][:28]))

print("\n=== Toute piece SD Worx a 591,86 ou proche ===")
for pid in [7040, 116212]:
    for i in call("account.move", "search_read",
                  [[["partner_id", "=", pid], ["move_type", "in", ["in_invoice", "in_refund"]]]],
                  {"fields": ["name", "ref", "invoice_date", "amount_total", "amount_residual",
                              "state", "payment_state"], "order": "invoice_date desc", "limit": 25}):
        flag = " <<<" if abs(abs(i["amount_total"]) - 591.86) < 60 else ""
        print("  %-6d %-14s %-12s %-11s tot=%9.2f res=%9.2f %s/%s%s" % (
            pid, i["name"], (i.get("ref") or "")[:12], i["invoice_date"], i["amount_total"],
            i["amount_residual"], i["state"], i["payment_state"], flag))

print("\n=== Precedents Bancontact petits achats ===")
for r in call("account.bank.statement.line", "search_read",
              [[["journal_id", "=", 14], ["payment_ref", "ilike", "Paiement Bancontact"],
                ["is_reconciled", "=", True]]],
              {"fields": ["id", "date", "amount", "move_id", "payment_ref"],
               "order": "date desc", "limit": 12}):
    ls = call("account.move.line", "search_read", [[["move_id", "=", r["move_id"][0]]]],
              {"fields": ["account_id", "partner_id"]})
    for l in ls:
        if not l["account_id"][1].startswith("55"):
            print("  %d %s %+8.2f -> %-34s | %s" % (
                r["id"], r["date"], r["amount"], l["account_id"][1][:34],
                r["payment_ref"][40:80]))

print("\n=== Partenaires cles ===")
for nm in ["Sendcloud", "Faire", "SD Worx", "Belfius Banque", "NOWJOBS", "Dragon Phenix"]:
    for p in call("res.partner", "search_read", [[["name", "ilike", nm]]],
                  {"fields": ["id", "name"], "limit": 5}):
        print("  #%-7d %s" % (p["id"], p["name"]))
