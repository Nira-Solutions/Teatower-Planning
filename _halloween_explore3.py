"""
Check BoMs for Halloween V0901, V0914 and supplier for MP_1V0914 (Halloween 2025).
Also check taxes on V0918.
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

# 1. BoM for V0901 (Halloween pumpkin ed. limitée - old)
print("=== BoM for V0901 (tmpl_id=5226) ===")
boms = call('mrp.bom', 'search_read',
    [[['product_tmpl_id', '=', 5226]]],
    {'fields': ['id', 'product_tmpl_id', 'product_qty', 'product_uom_id', 'type', 'bom_line_ids']})
for b in boms:
    print(json.dumps(b, indent=2))
    if b.get('bom_line_ids'):
        lines = call('mrp.bom.line', 'search_read',
            [[['bom_id', '=', b['id']]]],
            {'fields': ['id', 'product_id', 'product_qty', 'product_uom_id']})
        print("  BoM lines:")
        for l in lines:
            print("  ", json.dumps(l, indent=2))

# 2. BoM for V0914 (Halloween 2025 = Infusion du Printemps 2026 ?)
# Wait, MP_1V0914 = "Halloween 2025" but V0914 = "Infusion du Printemps 2026"
# Let's find the V0 product corresponding to Halloween 2025 MP
print("\n=== BoM for V0914 (tmpl_id=10090, Infusion du Printemps 2026) ===")
boms2 = call('mrp.bom', 'search_read',
    [[['product_tmpl_id', '=', 10090]]],
    {'fields': ['id', 'product_tmpl_id', 'product_qty', 'product_uom_id', 'type', 'bom_line_ids']})
for b in boms2:
    print(json.dumps(b, indent=2))
    if b.get('bom_line_ids'):
        lines = call('mrp.bom.line', 'search_read',
            [[['bom_id', '=', b['id']]]],
            {'fields': ['id', 'product_id', 'product_qty', 'product_uom_id']})
        print("  BoM lines:")
        for l in lines:
            print("  ", json.dumps(l, indent=2))

# 3. Supplier info for MP_1V0914 (Halloween 2025, tmpl_id=10091)
print("\n=== Supplier info for MP_1V0914 (Halloween 2025, tmpl_id=10091) ===")
si = call('product.supplierinfo', 'search_read',
    [[['product_tmpl_id', '=', 10091]]],
    {'fields': ['id', 'partner_id', 'product_code', 'product_name', 'price', 'currency_id', 'min_qty', 'delay']})
for s in si:
    print(json.dumps(s, indent=2))

# 4. Also find the V0 halloween 2025 product
print("\n=== Search V0 product linked to Halloween 2025 ===")
v0_hall = call('product.template', 'search_read',
    [[['name', 'ilike', 'halloween 2025'], ['default_code', 'like', 'V0']]],
    {'fields': ['id', 'name', 'default_code', 'categ_id']})
for p in v0_hall:
    print(json.dumps(p, indent=2))

# 5. Taxes on V0918
print("\n=== Taxes on V0918 (tmpl_id=10422) ===")
v0918 = call('product.template', 'read', [[10422]],
    {'fields': ['id', 'name', 'taxes_id', 'supplier_taxes_id']})
print(json.dumps(v0918, indent=2))

# 6. Check all BoMs with "halloween" or look broader - search all boms
print("\n=== All BoMs (recent) ===")
all_boms = call('mrp.bom', 'search_read',
    [[]],
    {'fields': ['id', 'product_tmpl_id', 'product_qty', 'type', 'bom_line_ids'],
     'limit': 20, 'order': 'id desc'})
for b in all_boms:
    print(json.dumps(b, indent=2))

# 7. Packaging Halloween 2025 details
print("\n=== Packaging Halloween 2025 (tmpl_id=10106) ===")
pkg = call('product.template', 'read', [[10106]],
    {'fields': ['id', 'name', 'default_code', 'uom_id', 'type', 'standard_price']})
print(json.dumps(pkg, indent=2))

# 8. Packaging sachet Halloween Pumpkin (EM0065)
print("\n=== Packaging sachet Halloween Pumpkin EM0065 (tmpl_id=4556) ===")
pkg2 = call('product.template', 'read', [[4556]],
    {'fields': ['id', 'name', 'default_code', 'uom_id', 'type', 'standard_price']})
print(json.dumps(pkg2, indent=2))

# 9. product.product IDs for the packaging
print("\n=== product.product for Packaging Halloween 2025 ===")
prods = call('product.product', 'search_read',
    [[['product_tmpl_id', '=', 10106]]],
    {'fields': ['id', 'name', 'default_code']})
print(json.dumps(prods, indent=2))
