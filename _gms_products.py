"""Pull GMS products via multiple criteria, then merge."""
import xmlrpc.client, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(m,me,a,k=None): return models.execute_kw(DB,uid,PWD,m,me,a,k or {})

GMS_ROUTE_IDS=[12,42]

# A. via product.template route_ids
tmpl_ids = call("product.template","search",[[("route_ids","in",GMS_ROUTE_IDS)]],{})
print(f"templates with GMS route: {len(tmpl_ids)}")

# B. via stock.warehouse for "GMS"
whs = call("stock.warehouse","search_read",[[]], {"fields":["id","name","code"]})
print("warehouses:", whs)

# C. via stock.warehouse.orderpoint for GMS warehouse
gms_wh_ids=[w["id"] for w in whs if "GMS" in (w.get("name") or "").upper() or (w.get("code") or "").upper().startswith("GMS")]
print("GMS wh ids:", gms_wh_ids)
op_prod_ids=set()
if gms_wh_ids:
    ops=call("stock.warehouse.orderpoint","search_read",[[("warehouse_id","in",gms_wh_ids)]], {"fields":["id","product_id","warehouse_id"], "limit":5000})
    print(f"orderpoints GMS: {len(ops)}")
    for o in ops:
        if o.get("product_id"): op_prod_ids.add(o["product_id"][0])

# D. via SO lines on partners tagged "GMS" (id 27) or "Canal GMS" (id 88)
gms_partner_ids = call("res.partner","search",[[("category_id","in",[27,88])]], {})
print(f"GMS partners: {len(gms_partner_ids)}")
so_prod_ids=set()
if gms_partner_ids:
    # only confirmed orders
    sols = call("sale.order.line","search_read",
        [[("order_partner_id","in",gms_partner_ids),("state","in",["sale","done"])]],
        {"fields":["product_id"], "limit":50000})
    for l in sols:
        if l.get("product_id"): so_prod_ids.add(l["product_id"][0])
    print(f"products in GMS SO lines: {len(so_prod_ids)}")

# Merge: orderpoint products are the canonical "GMS catalog" (replenishment plan)
# Fallback also include SO products
canon_ids = op_prod_ids
print(f"\nCanonical GMS product set (via orderpoints): {len(canon_ids)}")
print(f"SO-derived GMS product set: {len(so_prod_ids)}")

# Read these products
ids_to_read = sorted(canon_ids if canon_ids else so_prod_ids)
prods = call("product.product","search_read",
    [[("id","in",ids_to_read),("active","=",True)]],
    {"fields":["id","default_code","barcode","name","display_name","categ_id","list_price","uom_id"]})
print(f"products read: {len(prods)}")

# Stats
no_ean=[p for p in prods if not p.get("barcode")]
no_code=[p for p in prods if not p.get("default_code")]
print(f"sans EAN: {len(no_ean)} / sans default_code: {len(no_code)}")

with open("_gms_products.json","w",encoding="utf-8") as f:
    json.dump(prods,f,ensure_ascii=False,indent=2)

print("\nÉchantillon (15):")
for p in sorted(prods,key=lambda x:(x.get("default_code") or ""))[:15]:
    print(f"  {(p.get('default_code') or '—'):18}  {(p.get('barcode') or '—'):16}  {p.get('name')}")
