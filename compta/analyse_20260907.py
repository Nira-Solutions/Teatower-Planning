# -*- coding: utf-8 -*-
"""Analyse lecture seule des nouvelles lignes bancaires depuis la passe du 03/09."""
import os, re, sys, json
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


NEW = [20726, 20742, 20743, 20744, 20745, 20746, 20756, 20757, 20760, 20762,
       20764, 20765, 20766, 20777, 20779, 20782, 20783, 20787, 20788, 20791,
       20793, 20794, 20795, 20796, 20797, 20800]

rows = call("account.bank.statement.line", "search_read", [[["id", "in", NEW]]],
            {"fields": ["id", "date", "payment_ref", "amount", "partner_id", "journal_id"],
             "order": "date asc, id asc"})

STRUCT = re.compile(r"(\d{3})[/\*\+ ]{0,3}(\d{4})[/\*\+ ]{0,3}(\d{5})")
INVREF = re.compile(r"(?:INV|RINV)/\d{4}/\d{4,5}|(?:R?INV)/\d\d-\d\d/\d{4}")
IBAN = re.compile(r"\b(BE\d{14})\b")

report = []
for r in rows:
    ref = (r.get("payment_ref") or "").replace("\n", " ")
    print("=" * 110)
    print("BSL %d  %s  %s  %+.2f" % (r["id"], r["journal_id"][1], r["date"], r["amount"]))
    print("  REF: %s" % ref)
    info = {"id": r["id"], "date": r["date"], "amount": r["amount"], "ref": ref, "cands": []}

    # 1. communication structuree
    for mm in STRUCT.finditer(ref):
        s = "%s/%s/%s" % mm.groups()
        for f in call("account.move", "search_read", [[["payment_reference", "like", s]]],
                      {"fields": ["name", "partner_id", "amount_total", "amount_residual",
                                  "state", "payment_state", "invoice_date", "move_type"]}):
            print("  [COMM %s] %s %s %s tot=%.2f res=%.2f %s/%s" % (
                s, f["name"], f["invoice_date"], f["partner_id"][1][:28],
                f["amount_total"], f["amount_residual"], f["state"], f["payment_state"]))
            info["cands"].append(("comm", s, f))

    # 2. numero de facture en clair
    for name in set(INVREF.findall(ref)):
        for f in call("account.move", "search_read", [[["name", "=", name]]],
                      {"fields": ["name", "partner_id", "amount_total", "amount_residual",
                                  "state", "payment_state", "invoice_date"]}):
            print("  [REF %s] %s %s tot=%.2f res=%.2f %s/%s" % (
                name, f["invoice_date"], f["partner_id"][1][:28], f["amount_total"],
                f["amount_residual"], f["state"], f["payment_state"]))
            info["cands"].append(("ref", name, f))

    # 3. IBAN payeur
    for ib in set(IBAN.findall(ref.replace(" ", ""))):
        for b in call("res.partner.bank", "search_read", [[["acc_number", "like", ib]]],
                      {"fields": ["acc_number", "partner_id"]}):
            print("  [IBAN %s] -> %s (#%d)" % (ib, b["partner_id"][1], b["partner_id"][0]))
            info["cands"].append(("iban", ib, b["partner_id"]))

    # 4. precedent : meme libelle deja traite
    key = re.sub(r"[\d/:\-\.]+", " ", ref)[:40].strip()
    if key:
        prev = call("account.bank.statement.line", "search_read",
                    [[["journal_id", "in", [14, 36]], ["is_reconciled", "=", True],
                      ["payment_ref", "ilike", key], ["id", "!=", r["id"]]]],
                    {"fields": ["id", "date", "amount", "move_id"], "order": "date desc", "limit": 3})
        for p in prev:
            b = call("account.move.line", "search_read", [[["move_id", "=", p["move_id"][0]]]],
                     {"fields": ["account_id", "partner_id", "balance"]})
            dest = [l for l in b if not l["account_id"][1].startswith("55")
                    and not l["account_id"][1].startswith("58300")]
            for d in dest:
                print("  [PREC %d %s %+.2f] -> %s | %s" % (
                    p["id"], p["date"], p["amount"], d["account_id"][1][:40],
                    (d.get("partner_id") or [0, "-"])[1]))
            info["cands"].append(("prec", p["id"], [d["account_id"] for d in dest]))
    report.append(info)

json.dump(report, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "_analyse_20260907.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=str)
print("\nOK")
