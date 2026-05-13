"""
Explore existing MP_1V* and V0* products to copy structure for Halloween 2026.
"""
import xmlrpc.client
import json

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)

print(f"=== UID: {uid} ===\n")

# 1. Find existing MP_1V* products (raw materials)
mp_products = call('product.template', 'search_read',
    [[['default_code', 'like', 'MP_1V0']]],
    {'fields': ['id', 'name', 'default_code', 'categ_id', 'uom_id', 'uom_po_id',
                'standard_price', 'purchase_ok', 'sale_ok', 'type', 'route_ids'],
     'limit': 10})

print("=== MP_1V* products ===")
for p in mp_products:
    print(json.dumps(p, indent=2))

# 2. Find existing V0* finished products (vrac sachets)
v0_products = call('product.template', 'search_read',
    [[['default_code', 'like', 'V0']]],
    {'fields': ['id', 'name', 'default_code', 'categ_id', 'uom_id', 'uom_po_id',
                'list_price', 'standard_price', 'sale_ok', 'purchase_ok', 'type', 'route_ids'],
     'limit': 10,
     'order': 'default_code desc'})

print("\n=== V0* products (recent) ===")
for p in v0_products:
    print(json.dumps(p, indent=2))
