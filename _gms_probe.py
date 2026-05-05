"""Probe Odoo to find GMS criteria (route / pricelist / category / tag)."""
import xmlrpc.client, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(m,me,a,k=None): return models.execute_kw(DB,uid,PWD,m,me,a,k or {})

print("== Routes ==")
for r in call("stock.route","search_read",[[]], {"fields":["id","name","active"]}):
    print(" ",r)

print("\n== Pricelists ==")
for p in call("product.pricelist","search_read",[[]], {"fields":["id","name","active","currency_id"]}):
    print(" ",p)

print("\n== Product categories ==")
for c in call("product.category","search_read",[[]], {"fields":["id","name","parent_id"]}):
    print(" ",c)

print("\n== POS / product tags (product.tag) ==")
try:
    for t in call("product.tag","search_read",[[]], {"fields":["id","name"]}):
        print(" ",t)
except Exception as e:
    print(" no product.tag", e)

print("\n== Partner categories (res.partner.category) ==")
for t in call("res.partner.category","search_read",[[]], {"fields":["id","name","color","parent_id"]}):
    print(" ",t)
