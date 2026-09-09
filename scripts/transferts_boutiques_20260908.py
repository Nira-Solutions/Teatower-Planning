# -*- coding: utf-8 -*-
"""Transferts internes TT/Stock -> Rocourt / Liege / Namur, 8 u par reference."""
import os
import xmlrpc.client, os
url="https://tea-tree.odoo.com"; db="tsc-be-tea-tree-main-18515272"
user="nicolas.raes@teatower.com"; pw=os.environ["ODOO_PWD"]
uid = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common').authenticate(db,user,pw,{})
m = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
def X(model, method, *a, **kw):
    return m.execute_kw(db, uid, pw, model, method, list(a), kw)

CODES = ['V0700','V0825','V0836','V0863','V0869','V0816','V0845','V0846','V0778']
QTY = 8
SRC = 8  # TT/Stock
DESTS = [
    ("ROC",   104, 4712),
    ("LIEGE",  30, 4524),
    ("NAM",    56, 4540),
]

prods = X('product.product','search_read',[['default_code','in',CODES]],
          fields=['default_code','name','uom_id'])
by_code = {p['default_code']: p for p in prods}
assert len(by_code) == len(CODES), sorted(set(CODES)-set(by_code))

for code, ptype, dest in DESTS:
    moves = []
    for c in CODES:
        p = by_code[c]
        moves.append((0,0,{
            'product_id': p['id'],
            'product_uom_qty': QTY,
            'product_uom': p['uom_id'][0],
            'name': p['name'],
            'location_id': SRC,
            'location_dest_id': dest,
        }))
    pid = X('stock.picking','create',{
        'picking_type_id': ptype,
        'location_id': SRC,
        'location_dest_id': dest,
        'priority': '1',
        'move_ids_without_package': moves,
    })
    try:
        X('stock.picking','action_confirm',[pid])
    except xmlrpc.client.Fault as e:
        if 'cannot marshal None' not in str(e): raise
    try:
        X('stock.picking','action_assign',[pid])
    except xmlrpc.client.Fault as e:
        if 'cannot marshal None' not in str(e): raise
    rec = X('stock.picking','read',[pid],fields=['name','state','priority','location_id','location_dest_id'])[0]
    print(code, "->", rec['name'], "id", pid, "state", rec['state'], "prio", rec['priority'])
