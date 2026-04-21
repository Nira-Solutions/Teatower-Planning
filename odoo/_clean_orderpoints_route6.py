"""
Anti-récidive : orderpoints pointant route_id=6 hors template C0200 (10485).
→ route_id=False (scheduler tombera sur route par défaut, pas Manufacture).
"""
import xmlrpc.client, json
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

KEEP_TMPL = 10485  # C0200

# Tous OP avec route_id=6
ops = call("stock.warehouse.orderpoint","search_read",
    [[("route_id","=",6)]],
    {"fields":["id","name","product_id","route_id"]})

print(f"Orderpoints avec route_id=6 : {len(ops)}")

# Filtrer ceux dont product.product.product_tmpl_id != 10485
prod_ids = list({o["product_id"][0] for o in ops if o["product_id"]})
prods = call("product.product","read",[prod_ids, ["id","product_tmpl_id","default_code"]])
tmpl_by_prod = {p["id"]: p["product_tmpl_id"][0] for p in prods}

to_clear = []
keep_count = 0
for o in ops:
    pid = o["product_id"][0] if o["product_id"] else None
    tmpl = tmpl_by_prod.get(pid)
    if tmpl == KEEP_TMPL:
        keep_count += 1
    else:
        to_clear.append(o["id"])

print(f"À garder (C0200) : {keep_count}")
print(f"À nettoyer : {len(to_clear)}")

if to_clear:
    # chunks de 200
    ok = 0
    for i in range(0, len(to_clear), 200):
        chunk = to_clear[i:i+200]
        call("stock.warehouse.orderpoint","write",[chunk, {"route_id": False}])
        ok += len(chunk)
        print(f"  write OK : {ok}/{len(to_clear)}")
    print(f"Nettoyés : {ok}")

# Vérif finale
remain = call("stock.warehouse.orderpoint","search_count",[[("route_id","=",6)]])
print(f"\nOrderpoints route_id=6 APRÈS : {remain} (attendu = {keep_count})")
