# -*- coding: utf-8 -*-
"""Analyse lecture seule des nouvelles lignes bancaires (depuis la passe du 01/09)."""
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

NEW = [20689, 20690, 20691, 20692, 20698, 20703, 20716, 20717, 20718, 20719, 20720]
rows = call("account.bank.statement.line", "read", [NEW],
            {"fields": ["id", "date", "payment_ref", "amount", "partner_id", "journal_id"]})

for r in sorted(rows, key=lambda x: x["id"]):
    pr = (r.get("payment_ref") or "").replace("\n", " ")
    print("=" * 100)
    print("BSL %d  %s  %s  %+.2f  partner=%s" % (
        r["id"], r["journal_id"][1], r["date"], r["amount"],
        (r.get("partner_id") or [0, "-"])[1]))
    print("  REF: %s" % pr)

    # communication structuree
    for s in re.findall(r"\+\+\+(\d{3}/\d{4}/\d{5})\+\+\+", pr):
        key = "+++%s+++" % s
        mv = call("account.move", "search_read",
                  [["|", ["payment_reference", "like", s],
                         ["payment_reference", "like", key]]],
                  {"fields": ["name", "partner_id", "amount_total", "amount_residual",
                              "payment_state", "state", "invoice_date"]})
        print("  -> comm structuree %s : %s" % (s, mv or "AUCUNE"))

    # precedents sur libelle proche
    core = re.sub(r"\s+", " ", pr)[:40]
    prev = call("account.bank.statement.line", "search_read",
                [[["journal_id", "in", [14, 36]], ["is_reconciled", "=", True],
                  ["payment_ref", "ilike", core[:28]], ["id", "!=", r["id"]]]],
                {"fields": ["id", "date", "amount"], "limit": 3, "order": "date desc"})
    if prev:
        for p in prev:
            ml = call("account.move.line", "search_read",
                      [[["move_id.statement_line_id", "=", p["id"]]]],
                      {"fields": ["account_id", "partner_id", "balance"]})
            print("  PRECEDENT BSL %d %s %+.2f -> %s" % (
                p["id"], p["date"], p["amount"],
                [(x["account_id"][1], (x.get("partner_id") or [0, "-"])[1], x["balance"]) for x in ml]))
