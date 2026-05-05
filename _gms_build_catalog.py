"""Build the unified GMS catalog: union of (orderpoint GMS) + (SO lines GMS partners 12m)."""
import xmlrpc.client, sys, io, json, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(m,me,a,k=None): return models.execute_kw(DB,uid,PWD,m,me,a,k or {})

GMS_WH=2  # Stock Merchandiser code=GMS
GMS_PARTNER_TAGS=[27,88]  # GMS, Canal GMS

# A. Réappro orderpoints
ops=call("stock.warehouse.orderpoint","search_read",
    [[("warehouse_id","=",GMS_WH)]],{"fields":["product_id"],"limit":5000})
reappro_ids={o["product_id"][0] for o in ops if o.get("product_id")}

# B. Vendus à clients GMS 12 derniers mois
since=(dt.date.today()-dt.timedelta(days=365)).isoformat()
gms_partners=call("res.partner","search",[[("category_id","in",GMS_PARTNER_TAGS)]],{})
sols=call("sale.order.line","search_read",
    [[("order_partner_id","in",gms_partners),
      ("state","in",["sale","done"]),
      ("create_date",">=",since)]],
    {"fields":["product_id","product_uom_qty","price_subtotal"], "limit":100000})
vendu_qty={}
vendu_ca={}
for l in sols:
    pid=l.get("product_id")
    if not pid: continue
    pid=pid[0]
    vendu_qty[pid]=vendu_qty.get(pid,0)+(l.get("product_uom_qty") or 0)
    vendu_ca[pid]=vendu_ca.get(pid,0)+(l.get("price_subtotal") or 0)
vendu_ids=set(vendu_qty.keys())

all_ids=sorted(reappro_ids | vendu_ids)
print(f"Réappro orderpoint GMS: {len(reappro_ids)}")
print(f"Vendus 12m clients GMS:  {len(vendu_ids)}")
print(f"Union:                   {len(all_ids)}")

prods=call("product.product","search_read",
    [[("id","in",all_ids),("active","=",True)]],
    {"fields":["id","default_code","barcode","name","display_name","categ_id","list_price","uom_id","image_1920","product_tmpl_id"]})
print(f"products read (active): {len(prods)}")

# Build catalog rows
def is_service(p):
    code=(p.get("default_code") or "").upper().strip()
    name=(p.get("name") or "").lower()
    if code in ("TRANSPORT","SERVICE","REMISE","DEPLACEMENT","DÉPLACEMENT"): return True
    if code.startswith("DEL") or code.startswith("FRAIS"): return True
    if "transport" in name or "livraison" in name and "kit" not in name: return True
    return False

catalog=[]
for p in prods:
    if is_service(p): continue
    pid=p["id"]
    catalog.append({
        "id": pid,
        "code": p.get("default_code") or "",
        "ean": p.get("barcode") or "",
        "name": p.get("name") or "",
        "categ": (p.get("categ_id") or [None,""])[1] if p.get("categ_id") else "",
        "uom": (p.get("uom_id") or [None,""])[1] if p.get("uom_id") else "",
        "price": round(p.get("list_price") or 0, 2),
        "reappro": pid in reappro_ids,
        "qty12m": round(vendu_qty.get(pid,0), 1),
        "ca12m": round(vendu_ca.get(pid,0), 2),
    })

# sort: reappro first, then by code
catalog.sort(key=lambda x: (not x["reappro"], x["code"] or "ZZZ"))
with open("_gms_catalog.json","w",encoding="utf-8") as f:
    json.dump(catalog,f,ensure_ascii=False,indent=2)

print(f"\nCatalog written: {len(catalog)} rows")
print(f"sans EAN: {sum(1 for c in catalog if not c['ean'])}")
print(f"sans code: {sum(1 for c in catalog if not c['code'])}")
