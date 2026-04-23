"""
Hardening : garantir que la route Buy a priorite sur Manufacture.

Au niveau stock.rule.sequence :
  - Plus petit = plus prioritaire
  - Actuellement toutes les rules Buy et Manufacture ont sequence=20
  - On passe Buy rules a 10, Manufacture a 30
"""
import xmlrpc.client, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

# Buy rules (route_id=5)
buy_rule_ids = [7, 21, 33, 44, 55, 67, 79, 97]
mfg_rule_ids = [8, 18, 30, 41, 52, 64, 76, 94]

print("AVANT :", flush=True)
for r in call("stock.rule", "read", [buy_rule_ids + mfg_rule_ids,
                                       ["id", "name", "action", "sequence"]]):
    print(f"  {r['id']} | {r['name']} | seq={r['sequence']} | {r['action']}", flush=True)

# Write
call("stock.rule", "write", [buy_rule_ids, {"sequence": 10}])
call("stock.rule", "write", [mfg_rule_ids, {"sequence": 30}])

print("\nAPRES :", flush=True)
for r in call("stock.rule", "read", [buy_rule_ids + mfg_rule_ids,
                                       ["id", "name", "action", "sequence"]]):
    print(f"  {r['id']} | {r['name']} | seq={r['sequence']} | {r['action']}", flush=True)

print("\nDONE : Buy prioritaire sur Manufacture partout.", flush=True)
