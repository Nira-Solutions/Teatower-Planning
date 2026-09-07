# -*- coding: utf-8 -*-
"""Analyse 2 : cas a trancher (NowJobs, SumUp, SD Worx, salaires, Faire, Bancontact, KAIO)."""
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


def prec(pattern, label):
    print("\n--- PRECEDENTS %s ---" % label)
    rows = call("account.bank.statement.line", "search_read",
                [[["journal_id", "in", [14, 36]], ["is_reconciled", "=", True],
                  ["payment_ref", "ilike", pattern]]],
                {"fields": ["id", "date", "amount", "move_id", "payment_ref"],
                 "order": "date desc", "limit": 6})
    for p in rows:
        ls = call("account.move.line", "search_read", [[["move_id", "=", p["move_id"][0]]]],
                  {"fields": ["account_id", "partner_id", "balance", "full_reconcile_id"]})
        d = [l for l in ls if not l["account_id"][1].startswith("55")]
        for l in d:
            print("  %d %s %+10.2f -> %-38s %-30s rec=%s" % (
                p["id"], p["date"], p["amount"], l["account_id"][1][:38],
                (l.get("partner_id") or [0, "-"])[1][:30], bool(l.get("full_reconcile_id"))))


for pat, lab in [("NOW JOBS", "NowJobs"), ("SumUp Limited", "SumUp Belfius"),
                 ("SD Worx", "SD Worx"), ("ORDRE COLLECTIF SALAIRES", "Salaires Belfius"),
                 ("Faire 2595AN", "Faire achats"), ("EDENRED", "Edenred"),
                 ("BUREAU DURBUY", "Bureau Durbuy"), ("SANDWICH", "Sandwichs"),
                 ("Sendcloud", "Sendcloud"), ("Google Cloud", "Google Cloud")]:
    prec(pat, lab)

print("\n\n=== FACTURES FOURNISSEUR OUVERTES : NowJobs / SD Worx / Belfius / Sendcloud / Google ===")
for nm in ["NOWJOBS", "Now Jobs", "SD Worx", "Belfius", "Sendcloud", "Google"]:
    ps = call("res.partner", "search_read", [[["name", "ilike", nm]]], {"fields": ["id", "name"], "limit": 8})
    for p in ps:
        invs = call("account.move", "search_read",
                    [[["partner_id", "=", p["id"]], ["move_type", "in", ["in_invoice", "in_refund"]],
                      ["state", "in", ["posted", "draft"]], ["payment_state", "!=", "paid"]]],
                    {"fields": ["name", "ref", "invoice_date", "invoice_date_due", "amount_total",
                                "amount_residual", "state"], "order": "invoice_date desc", "limit": 8})
        if invs:
            print("\n  %s (#%d)" % (p["name"], p["id"]))
            for i in invs:
                print("    %-22s %-16s %s due=%s tot=%9.2f res=%9.2f %s" % (
                    i["name"], (i.get("ref") or "")[:16], i["invoice_date"],
                    i["invoice_date_due"], i["amount_total"], i["amount_residual"], i["state"]))

print("\n\n=== KAIO Retail invest : pieces ouvertes ===")
p = call("res.partner", "search_read", [[["name", "ilike", "KAIO"]]], {"fields": ["id", "name"]})
for pp in p:
    invs = call("account.move", "search_read",
                [[["partner_id", "=", pp["id"]], ["move_type", "in", ["out_invoice", "out_refund"]],
                  ["state", "=", "posted"], ["payment_state", "!=", "paid"]]],
                {"fields": ["name", "invoice_date", "amount_total", "amount_residual", "payment_reference"],
                 "order": "invoice_date asc"})
    print("  %s (#%d)" % (pp["name"], pp["id"]))
    for i in invs:
        print("    %-18s %s tot=%9.2f res=%9.2f  %s" % (
            i["name"], i["invoice_date"], i["amount_total"], i["amount_residual"],
            i.get("payment_reference")))
