"""
Diagnostic etape 2 : pourquoi action_replenish retourne False sur les 1V0
malgre la route Manufacture sur les templates.
"""
import xmlrpc.client, json
from collections import Counter

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PW = "Teatower123"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PW, {})
m = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)
def call(model, method, args=None, kwargs=None):
    return m.execute_kw(DB, uid, PW, model, method, args or [], kwargs or {})

print(f"UID = {uid}")

# 1) Variantes 1V0 - check route_ids HERITAGE vs route_from_categ
v_ids = call('product.product', 'search', [[('default_code', '=ilike', '1V0%')]])
print(f"\nVariantes 1V0 : {len(v_ids)}")
v_data = call('product.product', 'read', [v_ids],
              {'fields': ['id', 'default_code', 'route_ids', 'product_tmpl_id']})

route_dist = Counter()
for v in v_data:
    rs = tuple(sorted(v.get('route_ids') or []))
    route_dist[rs] += 1
print("Distribution route_ids variantes 1V0:")
for rs, c in route_dist.most_common():
    print(f"  {rs}: {c}")

# Echantillon
print("\nÉchantillon 5 variantes 1V0:")
for v in v_data[:5]:
    print(f"  {v['id']} {v['default_code']:10s} routes={v['route_ids']} tmpl={v['product_tmpl_id'][0]}")

# 2) Rules de la route Manufacture (id=6)
print("\n=== Rules de la route Manufacture (id=6) ===")
rules = call('stock.rule', 'search_read',
             [[('route_id', '=', 6)]],
             {'fields': ['id', 'name', 'action', 'location_dest_id', 'location_src_id',
                         'warehouse_id', 'company_id', 'active']})
print(f"Rules Manufacture : {len(rules)}")
for r in rules:
    print(f"  Rule {r['id']} {r['name'][:60]:60s} action={r['action']} "
          f"loc_dest={r.get('location_dest_id')} wh={r.get('warehouse_id')} active={r['active']}")

# 3) WH TT - verifier manufacture_to_resupply et resupply_route_ids
print("\n=== WH TT detail ===")
wh_tt = call('stock.warehouse', 'read', [[1]],
             {'fields': ['id', 'code', 'name', 'route_ids', 'manufacture_to_resupply',
                         'manufacture_pull_id', 'manu_type_id', 'lot_stock_id', 'in_type_id', 'out_type_id']})
for w in wh_tt:
    print(f"  WH {w['id']} {w['code']} {w['name']}")
    for k, v in w.items():
        if k != 'id':
            print(f"    {k} = {v}")

# 4) Test stock.rule._get_rule pour un produit 1V0 et la location TT/Stock
print("\n=== Test resolution stock.rule pour 1V0617 (Liberté) ===")
op = call('stock.warehouse.orderpoint', 'search_read',
          [[('id', '=', 5122)]],
          {'fields': ['id', 'product_id', 'location_id', 'route_id', 'rule_ids']})
print(f"OP/5122 : {op}")

# Lire le product.product 1V0617
p = call('product.product', 'read', [[op[0]['product_id'][0]]],
         {'fields': ['id', 'default_code', 'route_ids', 'route_from_categ_ids']})
print(f"Product : {p}")

# 5) Verifier la BoM de 1V0617
print("\n=== BoM de 1V0617 (Liberté) ===")
bom = call('mrp.bom', 'search_read',
           [[('product_tmpl_id.default_code', '=', '1V0617')]],
           {'fields': ['id', 'product_qty', 'product_uom_id', 'type', 'active', 'company_id', 'bom_line_ids']})
print(f"BoMs : {bom}")
if bom and bom[0].get('bom_line_ids'):
    lines = call('mrp.bom.line', 'read', [bom[0]['bom_line_ids']],
                 {'fields': ['id', 'product_id', 'product_qty', 'product_uom_id']})
    print(f"  Composants : {len(lines)}")
    for l in lines[:5]:
        print(f"    {l['product_id']} qty={l['product_qty']}")
