"""
Get BoM lines for recent saisonnier V0915, V0913 to understand the structure.
Also check supplier tax on MP_1V0914.
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

# BoM for V0915 (id=7675) lines
print("=== BoM lines for V0915 (bom_id=7675) ===")
lines = call('mrp.bom.line', 'search_read',
    [[['bom_id', '=', 7675]]],
    {'fields': ['id', 'product_id', 'product_qty', 'product_uom_id']})
for l in lines:
    print(json.dumps(l, indent=2))

# BoM for V0913 (id=7671) lines
print("\n=== BoM lines for V0913 (bom_id=7671) ===")
lines2 = call('mrp.bom.line', 'search_read',
    [[['bom_id', '=', 7671]]],
    {'fields': ['id', 'product_id', 'product_qty', 'product_uom_id']})
for l in lines2:
    print(json.dumps(l, indent=2))

# BoM for old V0901 - already gotten, BoM qty=1000 with MP qty=50 and packaging qty=1000
# So 1 sachet = 50/1000 = 0.05 kg of MP and 1 packaging

# Check if V0914 BoM lines are in units (not kg)
# V0914 BoM: product_qty=1500, MP qty=120, packaging qty=1500
# That means 1 sachet = 120/1500 = 0.08 kg ?
# Wait this BoM produces 1500 sachets from 120 units of MP?
# In the old system: MP units = kg equivalent?
# Let's check the MP_1V0914 UoM
print("\n=== MP_1V0914 full details ===")
mp914 = call('product.template', 'read', [[10091]],
    {'fields': ['id', 'name', 'default_code', 'uom_id', 'uom_po_id', 'standard_price', 'type']})
print(json.dumps(mp914, indent=2))

# Also check MP_1V0901
print("\n=== MP_1V0901 full details ===")
mp901 = call('product.template', 'read', [[5008]],
    {'fields': ['id', 'name', 'default_code', 'uom_id', 'uom_po_id', 'standard_price', 'type']})
print(json.dumps(mp901, indent=2))

# Also check MP_1V0918 (Au coin du feu) full details
print("\n=== MP_1V0918 full details ===")
mp918 = call('product.template', 'read', [[10414]],
    {'fields': ['id', 'name', 'default_code', 'uom_id', 'uom_po_id', 'standard_price', 'type']})
print(json.dumps(mp918, indent=2))

# product.product (variant) for MP_1V0918
print("\n=== product.product variant for MP_1V0918 ===")
pp = call('product.product', 'search_read',
    [[['product_tmpl_id', '=', 10414]]],
    {'fields': ['id', 'name', 'default_code']})
print(json.dumps(pp, indent=2))

# Check BoMs for V0918 - try by product.product
print("\n=== BoM search for V0918 by product_id ===")
pp918 = call('product.product', 'search_read',
    [[['product_tmpl_id', '=', 10422]]],
    {'fields': ['id', 'name', 'default_code']})
print("V0918 product.product:", json.dumps(pp918, indent=2))

if pp918:
    boms_pp = call('mrp.bom', 'search_read',
        [[['product_id', '=', pp918[0]['id']]]],
        {'fields': ['id', 'product_tmpl_id', 'product_id', 'product_qty', 'type', 'bom_line_ids']})
    print("BoMs by product_id:", json.dumps(boms_pp, indent=2))

# Check taxes on V0913 (saisonnier Noël)
print("\n=== Taxes on V0913 and V0915 ===")
v0913 = call('product.template', 'read', [[10146]],
    {'fields': ['id', 'name', 'taxes_id', 'supplier_taxes_id']})
print("V0913:", json.dumps(v0913, indent=2))

v0915 = call('product.template', 'read', [[10192]],
    {'fields': ['id', 'name', 'taxes_id', 'supplier_taxes_id']})
print("V0915:", json.dumps(v0915, indent=2))

# Check categ for V0913 and V0917/V0918
print("\n=== categ_id details for seasonal products ===")
# categ 1 = All (used for V0918/V0917/V0914)
# categ 75 = noel 2025 (used for V0913/V0905)
# Need a halloween category?
cats = call('product.category', 'search_read',
    [[['name', 'ilike', 'halloween']]],
    {'fields': ['id', 'name', 'complete_name', 'parent_id']})
print("Halloween categories:", json.dumps(cats, indent=2))
