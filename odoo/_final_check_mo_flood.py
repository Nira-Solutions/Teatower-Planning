import xmlrpc.client
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

total = call("mrp.production","search_count",[[("create_date",">=","2026-04-21 12:00:00")]])
cancel = call("mrp.production","search_count",[[("create_date",">=","2026-04-21 12:00:00"),("state","=","cancel")]])
by_state = {}
for s in ["draft","confirmed","progress","to_close","done","cancel"]:
    by_state[s] = call("mrp.production","search_count",[[("create_date",">=","2026-04-21 12:00:00"),("state","=",s)]])
print(f"Total MO créés après 12:00 : {total}")
print(f"Dont cancel : {cancel}")
print(f"Par état : {by_state}")
