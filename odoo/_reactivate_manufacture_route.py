"""
Reactivation route Manufacture/Fabriquer sur tea-tree.odoo.com
Demande Nicolas 2026-04-21 - contexte BoM C0200 id 7681 OK mais pas de route active.
"""
import xmlrpc.client
import json
import sys

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
print(f"UID auth: {uid}", flush=True)
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})


TPL_ID = 10485
OP_ID = 18791

print("\n=== STEP 1a: Search stock.route Manufacture/Fabriquer (active + archived) ===", flush=True)
route_ids = call(
    "stock.route",
    "search",
    [[("name", "in", ["Manufacture", "Fabriquer", "Fabrication", "Manufacturing"])]],
    {"context": {"active_test": False}},
)
print(f"route_ids found: {route_ids}", flush=True)

routes = []
if route_ids:
    routes = call(
        "stock.route",
        "read",
        [route_ids, ["id", "name", "active", "product_selectable", "product_categ_selectable", "warehouse_selectable", "sequence", "company_id"]],
        {"context": {"active_test": False}},
    )
    print(json.dumps(routes, indent=2, default=str), flush=True)

print("\n=== STEP 1b: Search stock.rule action=manufacture (active + archived) ===", flush=True)
rule_ids = call(
    "stock.rule",
    "search",
    [[("action", "=", "manufacture")]],
    {"context": {"active_test": False}},
)
print(f"rule_ids found: {rule_ids}", flush=True)

rules = []
if rule_ids:
    rules = call(
        "stock.rule",
        "read",
        [rule_ids, ["id", "name", "active", "action", "location_dest_id", "route_id", "picking_type_id", "company_id"]],
        {"context": {"active_test": False}},
    )
    print(json.dumps(rules, indent=2, default=str), flush=True)

print("\n=== STEP 1c: Module mrp status ===", flush=True)
mrp_mod = call("ir.module.module", "search_read", [[("name", "=", "mrp")], ["id", "name", "state", "shortdesc"]])
print(json.dumps(mrp_mod, indent=2, default=str), flush=True)

# Save snapshot
out = {
    "routes_found": routes,
    "rules_found": rules,
    "mrp_module": mrp_mod,
}
with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/_manufacture_route_diag.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str)

print("\nDiag saved.", flush=True)
