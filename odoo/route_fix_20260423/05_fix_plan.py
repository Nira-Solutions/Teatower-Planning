"""
Plan de correction. LECTURE SEULE (pas de write).

Objectif :
1. Reactiver route Buy (id=5) + ses 8 rules
2. Retirer route Manufacture (id=6) du warehouse.route_ids TT (1), GMS (2), Sales (7)
3. Laisser la route Manufacture (6) active pour C0200 (seul produit legit)
4. Nettoyer les 6 orderpoints qui ont encore route_id=6
5. Cancel + unlink des 18 MO du jour (state draft/confirmed)

Affiche le plan detaille pour validation.
"""
import xmlrpc.client, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

plan = {}

# === PLAN STEP 1 : Buy route + rules ===
print("=== STEP 1 : Reactiver route Buy (5) + ses 8 rules ===", flush=True)
buy_route = call("stock.route", "read", [[5], ["id", "name", "active", "rule_ids"]], {"context": {"active_test": False}})[0]
print(f"Route Buy : active={buy_route['active']} | rules={buy_route['rule_ids']}", flush=True)
buy_rules = call("stock.rule", "read", [buy_route["rule_ids"],
                 ["id", "name", "active", "action", "location_dest_id"]],
                 {"context": {"active_test": False}})
for r in buy_rules:
    print(f"  rule {r['id']} {r['name']} active={r['active']} action={r['action']}", flush=True)
plan["step1"] = {"route_id": 5, "rules_ids": buy_route["rule_ids"], "before": buy_rules}

# === PLAN STEP 2 : Warehouse TT/GMS/Sales route_ids contient 6 ? ===
print("\n=== STEP 2 : Warehouse.route_ids ===", flush=True)
whs = call("stock.warehouse", "search_read", [[]],
           {"fields": ["id", "name", "code", "route_ids", "buy_to_resupply", "manufacture_to_resupply"]})
wh_impact = []
for w in whs:
    has6 = 6 in (w.get("route_ids") or [])
    has5 = 5 in (w.get("route_ids") or [])
    print(f"  {w['code']} (id={w['id']}) route_ids={w.get('route_ids')} (has6={has6}, has5={has5}) | buy={w['buy_to_resupply']} mfg={w['manufacture_to_resupply']}", flush=True)
    if has6:
        wh_impact.append(w)
plan["step2_warehouses_with_mfg"] = [{"id": w["id"], "code": w["code"], "route_ids": w["route_ids"]} for w in wh_impact]

# === PLAN STEP 3 : Orderpoints avec route_id=6 (hors C0200) ===
print("\n=== STEP 3 : Orderpoints route_id=6 ===", flush=True)
ops_6 = call("stock.warehouse.orderpoint", "search_read",
             [[("route_id", "=", 6)]],
             {"fields": ["id", "name", "product_id", "route_id", "warehouse_id"]})
print(f"Total OP avec route_id=6 : {len(ops_6)}", flush=True)
# Check lesquels sont C0200
c0200_tpl = 10485
c0200_prods = call("product.product", "search", [[("product_tmpl_id", "=", c0200_tpl)]])
print(f"product.product ids C0200 : {c0200_prods}", flush=True)
ops_to_clean = []
for o in ops_6:
    pid = o["product_id"][0] if o["product_id"] else None
    if pid in c0200_prods:
        print(f"  KEEP (C0200) : OP {o['name']} | prod={o['product_id']}", flush=True)
    else:
        print(f"  CLEAN : OP {o['name']} | prod={o['product_id']} | wh={o['warehouse_id']}", flush=True)
        ops_to_clean.append(o["id"])
plan["step3_ops_to_clean"] = ops_to_clean

# === PLAN STEP 4 : MO draft/confirmed du jour a annuler ===
print("\n=== STEP 4 : MO a annuler (aujourd'hui + hier, state draft/confirmed) ===", flush=True)
mo_live_ids = call("mrp.production", "search",
                   [[("create_date", ">=", "2026-04-22 00:00:00"), ("state", "in", ["draft", "confirmed"])]])
print(f"MO live a annuler : {len(mo_live_ids)}", flush=True)
if mo_live_ids:
    mos = call("mrp.production", "read", [mo_live_ids,
                ["id", "name", "product_id", "state", "create_date", "origin", "product_qty"]])
    for mo in mos[:20]:
        print(f"  {mo['name']} | {mo['product_id'][1]} | qty={mo['product_qty']} | state={mo['state']} | origin={mo['origin']}", flush=True)
plan["step4_mo_to_cancel"] = mo_live_ids

# === Safety check : aucun MO en progress/done du jour ===
mo_risky = call("mrp.production", "search_count",
                [[("create_date", ">=", "2026-04-22 00:00:00"), ("state", "in", ["progress", "to_close", "done"])]])
print(f"\nMO risky (progress/done) depuis 2026-04-22 : {mo_risky} (doit etre 0 pour safe)", flush=True)
plan["mo_risky"] = mo_risky

# Check : aucune raw move done sur les MO a annuler
if mo_live_ids:
    raw_done = call("stock.move", "search_count",
                    [[("raw_material_production_id", "in", mo_live_ids), ("state", "=", "done")]])
    print(f"Raw moves DONE sur MO live : {raw_done} (doit etre 0)", flush=True)
    plan["raw_moves_done"] = raw_done

# === STEP 5 : autres produits qui devraient etre Buy ===
# Templates avec seller_ids mais sans route_ids operationnelle
print("\n=== STEP 5 : produits sans route explicite (heriteront de WH) ===", flush=True)
# 934 templates avec seller, 500 sur 500 samplees ont route_ids=[] => masses ok
# Le fix warehouse + reactivation Buy suffit a regulariser.

with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423/plan.json", "w", encoding="utf-8") as f:
    json.dump(plan, f, indent=2, default=str, ensure_ascii=False)

print("\n=== RESUME PLAN ===", flush=True)
print(f"  STEP 1 : reactiver route Buy (5) + 8 rules -> write active=True", flush=True)
print(f"  STEP 2 : retirer route 6 de {len(wh_impact)} warehouses (TT / Stock Merchandiser / Sales)", flush=True)
print(f"  STEP 3 : clear route_id sur {len(ops_to_clean)} orderpoints (laisser False)", flush=True)
print(f"  STEP 4 : cancel + unlink {len(mo_live_ids)} MO draft/confirmed crees apres 2026-04-22", flush=True)
print(f"  STEP 5 : C0200 reste avec route Manufacture en direct (legit)", flush=True)
print(f"\n  SAFE CHECK : mo_risky={mo_risky}, raw_moves_done={plan.get('raw_moves_done',0)}", flush=True)
