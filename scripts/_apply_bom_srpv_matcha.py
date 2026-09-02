"""Cree les nomenclatures des 3 SRP Matcha (SRPV0895/0907/0910).

Methode : on ne devine rien. Chaque composant est repris de la BoM du produit
unitaire (V0895/V0907/V0910) et mis au prorata de 60 sachets (= 10 SRP de 6),
puis on ajoute les 2 composants presents dans les 17 BoM SRP existantes :
ES8 (etiquette) et CAS08A (carton SRP), 10 U chacun.

Usage: --apply pour ecrire (sinon dry-run).
"""
import sys, xmlrpc.client
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})
APPLY='--apply' in sys.argv

TARGETS=[('SRPV0895','V0895'),('SRPV0907','V0907'),('SRPV0910','V0910')]
SRP_QTY   = 10.0   # la BoM SRP produit 10 SRP
UNITS     = 60.0   # 10 SRP x 6 sachets
ES8, CAS08A = 4567, 7678
COMMON=[(ES8, SRP_QTY, 1), (CAS08A, SRP_QTY, 1)]

for srp_code, unit_code in TARGETS:
    srp=call('product.product','search_read',[[('default_code','=',srp_code)]],
             {'fields':['id','name','product_tmpl_id']})[0]
    if call('mrp.bom','search_count',[[('product_tmpl_id','=',srp['product_tmpl_id'][0])]]):
        print(f'=  {srp_code} : BoM deja presente -> ignore'); continue

    unit=call('product.product','search_read',[[('default_code','=',unit_code)]],{'fields':['id','product_tmpl_id']})[0]
    src=call('mrp.bom','search_read',[[('product_tmpl_id','=',unit['product_tmpl_id'][0])]],
             {'fields':['id','product_qty'],'limit':1})[0]
    lines=call('mrp.bom.line','search_read',[[('bom_id','=',src['id'])]],
               {'fields':['product_id','product_qty','product_uom_id','sequence'],'order':'sequence,id'})

    ratio = UNITS / src['product_qty']
    print(f"\n{srp_code} <- BoM {src['id']} de {unit_code} (base {src['product_qty']:.0f} U, ratio x{ratio:g})")
    vals=[]
    for l in lines:
        q = round(l['product_qty'] * ratio, 4)
        print(f"   - {l['product_id'][1]:55} {q:8g} {l['product_uom_id'][1]}")
        vals.append((0,0,{'product_id':l['product_id'][0],'product_qty':q,
                          'product_uom_id':l['product_uom_id'][0],'sequence':1}))
    for pid, q, uom in COMMON:
        nm=call('product.product','read',[[pid]],{'fields':['display_name']})[0]['display_name']
        print(f"   - {nm:55} {q:8g} Units")
        vals.append((0,0,{'product_id':pid,'product_qty':q,'product_uom_id':uom,'sequence':1}))

    if APPLY:
        bid=call('mrp.bom','create',[{
            'product_tmpl_id': srp['product_tmpl_id'][0], 'product_qty': SRP_QTY,
            'product_uom_id': 1, 'type': 'normal', 'consumption': 'warning',
            'ready_to_produce': 'all_available', 'company_id': 1, 'bom_line_ids': vals}])
        print(f'   -> BoM {bid} creee')

print('\n' + ('APPLIQUE.' if APPLY else 'DRY-RUN (relancer avec --apply).'))
