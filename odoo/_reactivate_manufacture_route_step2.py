"""
Step 2 : Reactivate route Manufacture (id 6) + all manufacture rules + attach to C0200 template.
"""
import xmlrpc.client
import json

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})


ROUTE_ID = 6
RULE_IDS = [8, 18, 30, 41, 52, 64, 76, 94]
TPL_ID = 10485
OP_ID = 18791

print("=== STEP 2a: Reactivate stock.route id 6 (Manufacture) ===", flush=True)
res_r = call("stock.route", "write", [[ROUTE_ID], {"active": True, "product_selectable": True}])
print(f"route write result: {res_r}", flush=True)

print("\n=== STEP 2b: Reactivate stock.rule ids (action=manufacture) ===", flush=True)
res_rules = call("stock.rule", "write", [RULE_IDS, {"active": True}])
print(f"rules write result: {res_rules}", flush=True)

print("\n=== STEP 2c: Re-read to confirm ===", flush=True)
route_after = call("stock.route", "read", [[ROUTE_ID], ["id", "name", "active", "product_selectable", "product_categ_selectable", "warehouse_selectable"]])
print(json.dumps(route_after, indent=2, default=str), flush=True)

rules_after = call("stock.rule", "read", [RULE_IDS, ["id", "name", "active", "action", "location_dest_id", "route_id"]])
print(json.dumps(rules_after, indent=2, default=str), flush=True)

print("\n=== STEP 3: Current route_ids on template 10485 (before) ===", flush=True)
tpl_before = call("product.template", "read", [[TPL_ID], ["id", "default_code", "name", "route_ids", "bom_ids", "bom_count"]])
print(json.dumps(tpl_before, indent=2, default=str), flush=True)

print("\n=== STEP 4: Attach route Manufacture (6) to template 10485 ===", flush=True)
existing_routes = tpl_before[0].get("route_ids", []) or []
if ROUTE_ID not in existing_routes:
    res_tpl = call("product.template", "write", [[TPL_ID], {"route_ids": [(4, ROUTE_ID)]}])
    print(f"template write result: {res_tpl}", flush=True)
else:
    print("route already attached, skipping write", flush=True)

tpl_after = call("product.template", "read", [[TPL_ID], ["id", "default_code", "name", "route_ids"]])
print(json.dumps(tpl_after, indent=2, default=str), flush=True)

# Resolve route names
route_names = call("stock.route", "read", [tpl_after[0]["route_ids"], ["id", "name", "active"]])
print("\nRoutes on template 10485:", flush=True)
print(json.dumps(route_names, indent=2, default=str), flush=True)

print("\n=== STEP 5: Verify orderpoint 18791 ===", flush=True)
op = call("stock.warehouse.orderpoint", "read", [[OP_ID], ["id", "name", "product_id", "warehouse_id", "location_id", "route_id", "qty_multiple", "product_min_qty", "product_max_qty"]])
print(json.dumps(op, indent=2, default=str), flush=True)

# List routes available for this product on the orderpoint (what selection proposes)
# Query rules that match this product's routes for the orderpoint's location
product_id = op[0]["product_id"][0] if op[0].get("product_id") else None
if product_id:
    # Product routes = template routes + category routes
    prod = call("product.product", "read", [[product_id], ["id", "default_code", "name", "route_ids", "product_tmpl_id"]])
    print("\nProduct.product data:", flush=True)
    print(json.dumps(prod, indent=2, default=str), flush=True)

print("\nDONE.", flush=True)
