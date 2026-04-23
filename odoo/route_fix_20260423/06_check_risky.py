"""Check les 4 MO risky pour ne pas les casser."""
import xmlrpc.client, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

risky = call("mrp.production", "search_read",
             [[("create_date", ">=", "2026-04-22 00:00:00"), ("state", "in", ["progress", "to_close", "done"])]],
             {"fields": ["id", "name", "product_id", "state", "create_date", "origin", "product_qty"]})
print(f"MO risky ({len(risky)}) :", flush=True)
for mo in risky:
    print(f"  {mo['name']} | {mo['product_id'][1]} | qty={mo['product_qty']} | state={mo['state']} | origin={mo['origin']}", flush=True)
