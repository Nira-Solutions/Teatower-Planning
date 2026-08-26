# -*- coding: utf-8 -*-
"""SCAN lecture seule des lignes bancaires non lettrees ING (14)."""
import os, json
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

JOURNALS = {14: "ING", 36: "BELFIUS"}
rows = call("account.bank.statement.line", "search_read",
            [[["journal_id", "in", list(JOURNALS)], ["is_reconciled", "=", False]]],
            {"fields": ["id","date","payment_ref","amount","partner_id","journal_id","ref","move_id"],
             "order": "date asc, id asc"})
print(f"TOTAL non lettrees ING+BELFIUS : {len(rows)}")
out=[]
for r in rows:
    j = JOURNALS[r["journal_id"][0]]
    ref = (r.get("payment_ref") or "").replace("\n"," ")
    out.append({"id":r["id"],"j":j,"date":r["date"],"amount":r["amount"],
                "partner":(r.get("partner_id") or [None,""])[1],"ref":ref})
    print(f"{r['id']:>6} {j:<8} {r['date']} {r['amount']:>11,.2f}  {(r.get('partner_id') or [0,''])[1][:26]:<26} | {ref[:130]}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"_scan_20260826.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
