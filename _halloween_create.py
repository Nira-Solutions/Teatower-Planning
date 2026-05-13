"""
Create Halloween 2026 products in Odoo:
1. MP_1V0919 (raw material)
2. V0919 (finished product + image upload)
3. BoM (without packaging - to clarify with Nicolas)
"""
import xmlrpc.client
import json
import base64
import os

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)

print(f"Authenticated as UID: {uid}\n")

# ============================================================
# 1. CREATE MP_1V0919 (raw material)
# ============================================================
# Check if already exists
existing_mp = call('product.template', 'search_read',
    [[['default_code', '=', 'MP_1V0919']]],
    {'fields': ['id', 'name', 'default_code']})
if existing_mp:
    print(f"MP_1V0919 already exists: {existing_mp[0]}")
    mp_tmpl_id = existing_mp[0]['id']
else:
    mp_vals = {
        'name': 'Halloween 2026 Vrac (MP V0919)',
        'default_code': 'MP_1V0919',
        'type': 'consu',          # consumable (same as all other MP_1V*)
        'categ_id': 71,           # All / Matière Première
        'uom_id': 1,              # Units (convention Odoo TT - same as all other MP)
        'uom_po_id': 1,           # Units
        'standard_price': 18.00,
        'purchase_ok': True,
        'sale_ok': False,
        'route_ids': [(4, 5)],    # route 5 = Buy (same as all other MP_1V*)
    }
    mp_tmpl_id = call('product.template', 'create', [mp_vals])
    print(f"Created MP_1V0919: product.template id = {mp_tmpl_id}")

# Get the product.product variant id for MP
mp_pp = call('product.product', 'search_read',
    [[['product_tmpl_id', '=', mp_tmpl_id]]],
    {'fields': ['id', 'default_code', 'name']})
print(f"MP_1V0919 product.product: {mp_pp}")
mp_pp_id = mp_pp[0]['id'] if mp_pp else None

# Create supplier info for MP_1V0919
# partner_id=3144 (Mount Everest Tea Company Gmbh = Kirchner)
# Check if supplierinfo already exists
existing_si = call('product.supplierinfo', 'search_read',
    [[['product_tmpl_id', '=', mp_tmpl_id]]],
    {'fields': ['id', 'partner_id', 'product_code', 'price']})
if existing_si:
    print(f"Supplierinfo already exists: {existing_si[0]}")
    si_id = existing_si[0]['id']
else:
    si_vals = {
        'product_tmpl_id': mp_tmpl_id,
        'partner_id': 3144,           # Mount Everest Tea Company Gmbh (Kirchner)
        'product_code': '23137',
        'product_name': 'Halloween 2026',
        'price': 18.00,
        'currency_id': 125,           # EUR
        'min_qty': 1.0,
        'delay': 15,                  # 15 days (same as MP_1V0914/V0918)
    }
    si_id = call('product.supplierinfo', 'create', [si_vals])
    print(f"Created supplierinfo id = {si_id}")

# Add note in description_purchase for the fournisseur URL
call('product.template', 'write', [[mp_tmpl_id], {
    'description_purchase': 'Fournisseur Kirchner Fischer / Mount Everest Tea. Réf. 23137. URL: https://shop.mount-everest-tea.com/FRA/27747/Item.aspx?FromNo=26646&ItemNo=23137'
}])
print("Updated description_purchase with supplier URL")

# ============================================================
# 2. CREATE V0919 (finished product)
# ============================================================
existing_v = call('product.template', 'search_read',
    [[['default_code', '=', 'V0919']]],
    {'fields': ['id', 'name', 'default_code']})
if existing_v:
    print(f"\nV0919 already exists: {existing_v[0]}")
    v_tmpl_id = existing_v[0]['id']
else:
    # Convention: V0917 = "Matin enneigé - 100g", V0918 = "Au coin du feu - 100g"
    # V0914 = "Halloween 2025" had "Infusion du Printemps 2026" as V0914
    # Wait - check: MP_1V0914 = "Halloween 2025" but V0914 = "Infusion du Printemps 2026"
    # That's because the codes don't always match names
    # V0919 should follow the recent pattern: name "Halloween 2026 - 100g"
    # Categ: V0918/V0917 use categ_id=1 (All), V0913 uses categ 75 (noel 2025)
    # No halloween category exists, use categ 1 (All) - Nicolas can refine later

    # Load image
    image_path = r"C:\Users\FlowUP\OneDrive\Teatower\halloween_pumpkin_10B.jpg"
    image_b64 = None
    if os.path.exists(image_path):
        img_size = os.path.getsize(image_path)
        print(f"\nImage file: {image_path} ({img_size:,} bytes)")
        with open(image_path, 'rb') as f:
            image_b64 = base64.b64encode(f.read()).decode('utf-8')
        print(f"Image base64 encoded, length: {len(image_b64)} chars")
    else:
        print(f"\nWARNING: Image not found at {image_path}")

    v_vals = {
        'name': 'Halloween 2026 - 100g',
        'default_code': 'V0919',
        'type': 'consu',          # consumable (same as all other V0xxx)
        'categ_id': 1,            # All (same as V0917/V0918)
        'uom_id': 1,              # Units
        'uom_po_id': 1,           # Units
        'sale_ok': True,
        'purchase_ok': True,      # same as other V0xxx (purchase_ok=True even if assembled)
        'list_price': 0.0,        # Nicolas will set price later
        'standard_price': 0.0,
        'taxes_id': [(6, 0, [8])],         # 6% tax (same as V0913/V0915/V0918)
        'supplier_taxes_id': [(6, 0, [18])], # supplier tax 18 (same as V0913/V0915/V0918)
        'route_ids': [(4, 5)],    # route 5 (same as V0918)
    }
    if image_b64:
        v_vals['image_1920'] = image_b64

    v_tmpl_id = call('product.template', 'create', [v_vals])
    print(f"\nCreated V0919: product.template id = {v_tmpl_id}")

# Get product.product variant
v_pp = call('product.product', 'search_read',
    [[['product_tmpl_id', '=', v_tmpl_id]]],
    {'fields': ['id', 'name', 'default_code']})
print(f"V0919 product.product: {v_pp}")
v_pp_id = v_pp[0]['id'] if v_pp else None

# ============================================================
# 3. CREATE BoM for V0919
# ============================================================
# Pattern from recent saisonniers:
# V0915 BoM: qty=100, MP=10 units, packaging=100 units
# V0913 BoM: qty=50, MP=5 units, packaging=50 units
# => Ratio = 1 MP unit per 10 sachets (or per 50, depending on batch size)
# V0914 (Halloween 2025) BoM: qty=1500, MP=120 units
# => 120/1500 = 0.08 kg per sachet???
# Wait - looking at V0915: qty=100 sachets, MP=10 units
# If sachets are 100g each, then 10 sachets = 1 kg = 1 unit of MP
# So 1 unit MP = 1 kg. Convention: MP units are equivalent to kg in this system.
# For V0919 (100g sachet): BoM of 100 sachets needs 10 units of MP_1V0919

# Check existing BoM for V0919
existing_bom = call('mrp.bom', 'search_read',
    [[['product_tmpl_id', '=', v_tmpl_id]]],
    {'fields': ['id', 'product_tmpl_id', 'product_qty', 'type']})
if existing_bom:
    print(f"\nBoM already exists: {existing_bom[0]}")
    bom_id = existing_bom[0]['id']
else:
    # BoM: 100 sachets from 10 units MP_1V0919 (+ packaging TODO)
    bom_vals = {
        'product_tmpl_id': v_tmpl_id,
        'product_qty': 100.0,
        'product_uom_id': 1,      # Units
        'type': 'normal',
        'bom_line_ids': [
            (0, 0, {
                'product_id': mp_pp_id,
                'product_qty': 10.0,
                'product_uom_id': 1,   # Units (= kg in TT convention)
            }),
            # Packaging Halloween 2026: NOT added yet - to clarify with Nicolas
            # Packaging Halloween 2025 (product.product id=7342) exists but no default_code
        ],
    }
    bom_id = call('mrp.bom', 'create', [bom_vals])
    print(f"\nCreated BoM id = {bom_id}")

# ============================================================
# 4. VERIFICATION - read back all created records
# ============================================================
print("\n" + "="*60)
print("VERIFICATION")
print("="*60)

mp_check = call('product.template', 'read', [[mp_tmpl_id]],
    {'fields': ['id', 'name', 'default_code', 'categ_id', 'uom_id', 'standard_price',
                'purchase_ok', 'sale_ok', 'type', 'description_purchase']})
print(f"\nMP_1V0919 template: {json.dumps(mp_check, indent=2)}")

si_check = call('product.supplierinfo', 'read', [[si_id]],
    {'fields': ['id', 'partner_id', 'product_code', 'product_name', 'price', 'min_qty', 'delay']})
print(f"\nSupplierinfo: {json.dumps(si_check, indent=2)}")

v_check = call('product.template', 'read', [[v_tmpl_id]],
    {'fields': ['id', 'name', 'default_code', 'categ_id', 'uom_id', 'list_price',
                'sale_ok', 'purchase_ok', 'type', 'taxes_id', 'image_1920']})
# Shorten image for display
if v_check[0].get('image_1920'):
    img_len = len(v_check[0]['image_1920'])
    v_check[0]['image_1920'] = f"<base64 {img_len} chars>"
print(f"\nV0919 template: {json.dumps(v_check, indent=2)}")

bom_check = call('mrp.bom', 'read', [[bom_id]],
    {'fields': ['id', 'product_tmpl_id', 'product_qty', 'product_uom_id', 'type', 'bom_line_ids']})
print(f"\nBoM: {json.dumps(bom_check, indent=2)}")

bom_lines = call('mrp.bom.line', 'search_read',
    [[['bom_id', '=', bom_id]]],
    {'fields': ['id', 'product_id', 'product_qty', 'product_uom_id']})
print(f"\nBoM lines: {json.dumps(bom_lines, indent=2)}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"MP_1V0919 product.template id: {mp_tmpl_id}")
print(f"MP_1V0919 product.product id: {mp_pp_id}")
print(f"Supplierinfo id: {si_id}")
print(f"V0919 product.template id: {v_tmpl_id}")
print(f"V0919 product.product id: {v_pp_id}")
print(f"BoM id: {bom_id}")
