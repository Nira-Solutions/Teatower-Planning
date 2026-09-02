"""Cree les regles de reappro min/max sur les SRP 6x VRAC qui n'en ont pas.
Perimetre : les 17 refs de la liste EAN du 02/09/2026 (SRPV0914 exclu, hors liste).
Regle : entrepot Teatower (TT) / TT/Stock, min 10, max 20, route Fabriquer, auto.
Usage: --apply pour ecrire (sinon dry-run).
"""
import sys, xmlrpc.client
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})
APPLY='--apply' in sys.argv

REFS=['SRPV0121','SRPV0205','SRPV0301','SRPV0600','SRPV0626','SRPV0628','SRPV0635',
      'SRPV0669','SRPV0723','SRPV0751','SRPV0832','SRPV0868','SRPV0878','SRPV0880',
      'SRPV0895','SRPV0907','SRPV0910']
WH, LOC, ROUTE = 1, 8, 6     # Teatower / TT/Stock / Manufacture
MIN, MAX = 10.0, 20.0

prods=call('product.product','search_read',[[('default_code','in',REFS)]],
           {'fields':['id','default_code','name','product_tmpl_id'],'order':'default_code'})
assert len(prods)==len(REFS), f'{len(prods)} produits trouves pour {len(REFS)} refs'
pids=[p['id'] for p in prods]

existing={o['product_id'][0] for o in call('stock.warehouse.orderpoint','search_read',
    [[('product_id','in',pids),('warehouse_id','=',WH)]],{'fields':['product_id']})}
bom_tmpl={b['product_tmpl_id'][0] for b in call('mrp.bom','search_read',
    [[('product_tmpl_id','in',[p['product_tmpl_id'][0] for p in prods])]],{'fields':['product_tmpl_id']})}

created=0; sans_bom=[]
for p in prods:
    if p['id'] in existing:
        print(f"=  {p['default_code']} : regle deja presente sur TT -> ignore"); continue
    bom = p['product_tmpl_id'][0] in bom_tmpl
    if not bom: sans_bom.append(p['default_code'])
    print(f"+  {p['default_code']} min {MIN:.0f} / max {MAX:.0f} TT/Stock route Fabriquer"
          f"{'   [!] SANS NOMENCLATURE' if not bom else ''}")
    if APPLY:
        call('stock.warehouse.orderpoint','create',[{
            'product_id': p['id'], 'warehouse_id': WH, 'location_id': LOC,
            'product_min_qty': MIN, 'product_max_qty': MAX,
            'qty_multiple': 1.0, 'route_id': ROUTE, 'trigger': 'auto', 'company_id': 1}])
    created+=1

print(f"\n{created} regle(s) {'creee(s)' if APPLY else 'a creer'}.")
if sans_bom: print(f"[!] Sans nomenclature, le reappro leverai une exception : {', '.join(sans_bom)}")
if not APPLY: print('DRY-RUN (relancer avec --apply).')
