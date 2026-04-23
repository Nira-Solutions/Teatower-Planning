"""
EXECUTION du plan de correction route Buy/Manufacture 2026-04-23.

1. Reactivate route Buy (5) + 8 rules
2. Remove route 6 from warehouse TT (1) route_ids
3. Clear route_id=False on 6 orderpoints (glaces GI0xxx)
4. Cancel + unlink 17 MO confirmed du 2026-04-22/23
5. C0200 : untouched (legit)

Safety :
- Vérif raw_moves done = 0 avant unlink
- Vérif mo_risky (done/progress) : laisses tranquilles
"""
import xmlrpc.client, json, sys, io
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

report = {"ts": datetime.now().isoformat(), "steps": []}

# ===== STEP 1 : Reactivate Buy route + rules =====
print("\n=== STEP 1 : Reactivate route Buy (5) ===", flush=True)
res1a = call("stock.route", "write", [[5], {"active": True}])
print(f"  route.write active=True : {res1a}", flush=True)
rules_buy = [7, 21, 33, 44, 55, 67, 79, 97]
res1b = call("stock.rule", "write", [rules_buy, {"active": True}])
print(f"  rules.write active=True : {res1b}", flush=True)

# Verif
buy_after = call("stock.route", "read", [[5], ["id", "name", "active"]])
rules_after = call("stock.rule", "read", [rules_buy, ["id", "name", "active"]])
print(f"  Route Buy APRES : {buy_after}", flush=True)
print(f"  Rules actifs : {sum(1 for r in rules_after if r['active'])}/{len(rules_after)}", flush=True)
report["steps"].append({"step": "1_reactivate_buy", "route": buy_after, "rules": rules_after})

# ===== STEP 2 : Remove route 6 from warehouse TT =====
print("\n=== STEP 2 : Retirer route 6 (Manufacture) du warehouse TT ===", flush=True)
wh_tt = call("stock.warehouse", "read", [[1], ["id", "name", "code", "route_ids"]])[0]
print(f"  AVANT : {wh_tt}", flush=True)
new_routes = [r for r in wh_tt["route_ids"] if r != 6]
res2 = call("stock.warehouse", "write", [[1], {"route_ids": [(6, 0, new_routes)]}])
print(f"  write result : {res2}", flush=True)
wh_tt_after = call("stock.warehouse", "read", [[1], ["id", "name", "code", "route_ids"]])[0]
print(f"  APRES : {wh_tt_after}", flush=True)
report["steps"].append({"step": "2_warehouse_tt", "before": wh_tt, "after": wh_tt_after})

# ===== STEP 3 : Clear route_id on 6 orderpoints =====
print("\n=== STEP 3 : Clear route_id sur 6 orderpoints ===", flush=True)
ops_to_clean = [5248, 5249, 5250, 5636, 5922, 18792]
ops_before = call("stock.warehouse.orderpoint", "read", [ops_to_clean,
                   ["id", "name", "product_id", "route_id"]])
print(f"  AVANT :", flush=True)
for o in ops_before:
    print(f"    {o['name']} | prod={o['product_id'][1] if o['product_id'] else '?'} | route={o['route_id']}", flush=True)
res3 = call("stock.warehouse.orderpoint", "write", [ops_to_clean, {"route_id": False}])
print(f"  write result : {res3}", flush=True)
ops_after = call("stock.warehouse.orderpoint", "read", [ops_to_clean,
                   ["id", "name", "product_id", "route_id"]])
print(f"  APRES :", flush=True)
for o in ops_after:
    print(f"    {o['name']} | route={o['route_id']}", flush=True)
report["steps"].append({"step": "3_orderpoints", "before": ops_before, "after": ops_after})

# ===== STEP 4 : Cancel + unlink 17 MO =====
print("\n=== STEP 4 : Cancel MO draft/confirmed depuis 2026-04-22 ===", flush=True)
mo_ids = call("mrp.production", "search",
              [[("create_date", ">=", "2026-04-22 00:00:00"), ("state", "in", ["draft", "confirmed"])]])
print(f"  MO a annuler : {len(mo_ids)}", flush=True)

# Double safety : raw done = 0
raw_done = call("stock.move", "search_count",
                [[("raw_material_production_id", "in", mo_ids), ("state", "=", "done")]])
print(f"  Raw moves done : {raw_done}", flush=True)
if raw_done > 0:
    print(f"  ABORT : raw moves done != 0", flush=True)
    with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423/execute_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str, ensure_ascii=False)
    sys.exit(1)

# Cancel
cancelled = 0
cancel_errors = []
for i in range(0, len(mo_ids), 50):
    chunk = mo_ids[i:i+50]
    try:
        call("mrp.production", "action_cancel", [chunk])
        cancelled += len(chunk)
        print(f"    cancel chunk {i}-{i+len(chunk)} OK", flush=True)
    except Exception as e:
        print(f"    cancel chunk {i} FAIL : {str(e)[:200]}", flush=True)
        for rid in chunk:
            try:
                call("mrp.production", "action_cancel", [[rid]])
                cancelled += 1
            except Exception as e2:
                cancel_errors.append({"id": rid, "error": str(e2)[:200]})
print(f"  Annules : {cancelled} / {len(mo_ids)} ; erreurs : {len(cancel_errors)}", flush=True)

# Unlink (seulement ceux state=cancel)
mo_cancel_ids = call("mrp.production", "search",
                     [[("create_date", ">=", "2026-04-22 00:00:00"), ("state", "=", "cancel"),
                       ("id", "in", mo_ids)]])
print(f"  MO cancel a unlink : {len(mo_cancel_ids)}", flush=True)
unlinked = 0
unlink_errors = []
for i in range(0, len(mo_cancel_ids), 50):
    chunk = mo_cancel_ids[i:i+50]
    try:
        call("mrp.production", "unlink", [chunk])
        unlinked += len(chunk)
        print(f"    unlink chunk {i}-{i+len(chunk)} OK", flush=True)
    except Exception as e:
        print(f"    unlink chunk {i} FAIL : {str(e)[:200]}", flush=True)
        for rid in chunk:
            try:
                call("mrp.production", "unlink", [[rid]])
                unlinked += 1
            except Exception as e2:
                unlink_errors.append({"id": rid, "error": str(e2)[:200]})
print(f"  Unlinked : {unlinked} / {len(mo_cancel_ids)} ; erreurs : {len(unlink_errors)}", flush=True)

report["steps"].append({
    "step": "4_mo_cleanup",
    "mo_targeted": mo_ids,
    "cancelled": cancelled,
    "cancel_errors": cancel_errors,
    "unlinked": unlinked,
    "unlink_errors": unlink_errors,
})

# ===== FINAL CHECK =====
print("\n=== FINAL CHECK ===", flush=True)
mo_remain = call("mrp.production", "search_count",
                 [[("create_date", ">=", "2026-04-22 00:00:00"), ("state", "in", ["draft", "confirmed"])]])
print(f"  MO draft/confirmed restants : {mo_remain} (attendu 0)", flush=True)
op_remain = call("stock.warehouse.orderpoint", "search_count", [[("route_id", "=", 6)]])
print(f"  Orderpoints route=6 restants : {op_remain} (attendu 0)", flush=True)
tpl_remain = call("product.template", "search_count", [[("route_ids", "in", [6])]])
print(f"  Templates route=6 restants : {tpl_remain} (attendu 1 = C0200)", flush=True)
wh_check = call("stock.warehouse", "read", [[1], ["route_ids"]])[0]
print(f"  WH TT route_ids : {wh_check['route_ids']} (doit pas contenir 6)", flush=True)
buy_check = call("stock.route", "read", [[5], ["active"]])[0]
print(f"  Route Buy active : {buy_check['active']} (doit etre True)", flush=True)

report["final_check"] = {
    "mo_remaining_draft_confirmed": mo_remain,
    "op_route_6_remaining": op_remain,
    "tpl_route_6_remaining": tpl_remain,
    "wh_tt_route_ids": wh_check["route_ids"],
    "route_buy_active": buy_check["active"],
}

with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423/execute_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, default=str, ensure_ascii=False)
print("\nRapport ecrit : odoo/route_fix_20260423/execute_report.json", flush=True)
print("DONE.", flush=True)
