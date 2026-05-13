"""
Deep explore: Kirchner supplier info, Halloween products, BoM of V0918, categories.
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

# 1. Find Kirchner Fischer / Mount Everest Tea supplier
print("=== Kirchner / Mount Everest partners ===")
partners = call('res.partner', 'search_read',
    [[['name', 'ilike', 'kirchner']]],
    {'fields': ['id', 'name', 'supplier_rank'], 'limit': 5})
for p in partners:
    print(json.dumps(p, indent=2))

partners2 = call('res.partner', 'search_read',
    [[['name', 'ilike', 'mount everest']]],
    {'fields': ['id', 'name', 'supplier_rank'], 'limit': 5})
for p in partners2:
    print(json.dumps(p, indent=2))

# 2. Find supplierinfo for MP_1V0918 (Au coin du feu - most recent saisonnier)
print("\n=== Supplier info for MP_1V0918 (id=10414) ===")
si = call('product.supplierinfo', 'search_read',
    [[['product_tmpl_id', '=', 10414]]],
    {'fields': ['id', 'partner_id', 'product_code', 'product_name', 'price', 'currency_id', 'min_qty', 'delay']})
for s in si:
    print(json.dumps(s, indent=2))

# 3. Search for any Halloween product
print("\n=== Halloween products ===")
halloween = call('product.template', 'search_read',
    [[['name', 'ilike', 'halloween']]],
    {'fields': ['id', 'name', 'default_code', 'categ_id', 'type'], 'limit': 10})
for p in halloween:
    print(json.dumps(p, indent=2))

# 4. Get BoM for V0918 (id=10422)
print("\n=== BoM for V0918 (product template id=10422) ===")
boms = call('mrp.bom', 'search_read',
    [[['product_tmpl_id', '=', 10422]]],
    {'fields': ['id', 'product_tmpl_id', 'product_id', 'product_qty', 'product_uom_id', 'type', 'bom_line_ids']})
for b in boms:
    print(json.dumps(b, indent=2))
    # Get bom lines
    if b.get('bom_line_ids'):
        lines = call('mrp.bom.line', 'search_read',
            [[['bom_id', '=', b['id']]]],
            {'fields': ['id', 'product_id', 'product_qty', 'product_uom_id']})
        print("  BoM lines:")
        for l in lines:
            print("  ", json.dumps(l, indent=2))

# 5. Also check BoM for V0917
print("\n=== BoM for V0917 (product template id=10421) ===")
boms2 = call('mrp.bom', 'search_read',
    [[['product_tmpl_id', '=', 10421]]],
    {'fields': ['id', 'product_tmpl_id', 'product_id', 'product_qty', 'product_uom_id', 'type', 'bom_line_ids']})
for b in boms2:
    print(json.dumps(b, indent=2))
    if b.get('bom_line_ids'):
        lines = call('mrp.bom.line', 'search_read',
            [[['bom_id', '=', b['id']]]],
            {'fields': ['id', 'product_id', 'product_qty', 'product_uom_id']})
        print("  BoM lines:")
        for l in lines:
            print("  ", json.dumps(l, indent=2))

# 6. List product categories
print("\n=== Product categories (saisonnier/halloween) ===")
cats = call('product.category', 'search_read',
    [[['name', 'ilike', 'halloween']]],
    {'fields': ['id', 'name', 'complete_name'], 'limit': 10})
for c in cats:
    print(json.dumps(c, indent=2))

cats2 = call('product.category', 'search_read',
    [[['name', 'ilike', 'saisonnier']]],
    {'fields': ['id', 'name', 'complete_name'], 'limit': 10})
for c in cats2:
    print(json.dumps(c, indent=2))

# Also get categ 75 (noel 2025) to understand naming pattern
cats3 = call('product.category', 'read', [[75]],
    {'fields': ['id', 'name', 'complete_name', 'parent_id']})
print("\n=== Categ 75 detail ===")
for c in cats3:
    print(json.dumps(c, indent=2))

# 7. UoM check - find 'unit'
print("\n=== UoM 'unit'/'units' ===")
uoms = call('uom.uom', 'search_read',
    [[['name', 'ilike', 'unit']]],
    {'fields': ['id', 'name', 'category_id'], 'limit': 5})
for u in uoms:
    print(json.dumps(u, indent=2))

# 8. Taxes
print("\n=== Taxes (vente, 6%, 21%) ===")
taxes = call('account.tax', 'search_read',
    [[['type_tax_use', '=', 'sale'], ['active', '=', True]]],
    {'fields': ['id', 'name', 'amount'], 'limit': 10})
for t in taxes:
    print(json.dumps(t, indent=2))
