"""
Verif : les rules de route Manufacture (6) sont-elles actives ?
Comparaison avec la doc Odoo : un orderpoint sans route_id resout via les routes
actives du produit (template > category > warehouse).
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

# Route Manufacture (6) : rules
r6 = call("stock.route", "read", [[6], ["id", "name", "active", "rule_ids"]])[0]
print(f"Route 6 : {r6}", flush=True)
rules6 = call("stock.rule", "read", [r6["rule_ids"], ["id", "name", "active", "action", "location_dest_id", "picking_type_id"]],
              {"context": {"active_test": False}})
print("\nRules route Manufacture :", flush=True)
for r in rules6:
    print(f"  id={r['id']} | {r['name']} | action={r['action']} | active={r['active']} | dest={r.get('location_dest_id')}", flush=True)

# Routes d'entrepot pour WH (TT)
print("\n=== Warehouses + leurs routes ===", flush=True)
whs = call("stock.warehouse", "search_read", [[]], {"fields": ["id", "name", "code", "route_ids", "buy_to_resupply", "manufacture_to_resupply", "reception_route_id", "delivery_route_id", "resupply_route_ids"]})
for w in whs:
    print(f"  {w['id']} | {w['name']} ({w['code']})", flush=True)
    print(f"    buy_to_resupply={w.get('buy_to_resupply')} | mfg_to_resupply={w.get('manufacture_to_resupply')}", flush=True)
    print(f"    route_ids={w.get('route_ids')}", flush=True)

# Orderpoint 5080 (OP/13504) : tracer route_compute
print("\n=== Orderpoint OP/13504 (05V0628) ===", flush=True)
op = call("stock.warehouse.orderpoint", "read", [[5080], ["id", "name", "product_id", "route_id", "warehouse_id", "location_id", "route_ids", "rule_ids"]])[0]
print(json.dumps(op, indent=2, default=str, ensure_ascii=False), flush=True)

# Check le produit 3969 (05V0628)
prod = call("product.product", "read", [[3969], ["id", "default_code", "name", "route_ids", "product_tmpl_id", "purchase_ok", "seller_ids"]])[0]
print(f"\nProduit 3969 : {prod}", flush=True)
tpl = call("product.template", "read", [[prod["product_tmpl_id"][0]], ["id", "default_code", "name", "route_ids", "categ_id", "purchase_ok"]])[0]
print(f"Template : {tpl}", flush=True)
cat = call("product.category", "read", [[tpl["categ_id"][0]], ["id", "name", "route_ids", "total_route_ids"]])[0]
print(f"Categorie : {cat}", flush=True)
if cat.get("total_route_ids"):
    trs = call("stock.route", "read", [cat["total_route_ids"], ["id", "name", "active"]], {"context": {"active_test": False}})
    print(f"Routes totales categorie :", flush=True)
    for t in trs:
        print(f"  {t}", flush=True)

# seller du produit
if prod.get("seller_ids"):
    sellers = call("product.supplierinfo", "read", [prod["seller_ids"], ["id", "partner_id", "price", "min_qty"]])
    print(f"\nSellers de 05V0628 : {sellers}", flush=True)
