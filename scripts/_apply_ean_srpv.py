"""Pose les codes EAN-13 sur les 17 SRP 6x VRAC (liste Nicolas 02/09/2026).
Usage: --apply pour ecrire (sinon dry-run).
"""
import sys, xmlrpc.client
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})
APPLY='--apply' in sys.argv

PAIRS=[('5413393004169','SRPV0121'),('5413393004176','SRPV0205'),('5413393004183','SRPV0301'),
('5413393004190','SRPV0600'),('5413393004206','SRPV0626'),('5413393004213','SRPV0628'),
('5413393004220','SRPV0635'),('5413393004237','SRPV0669'),('5413393004244','SRPV0723'),
('5413393004251','SRPV0751'),('5413393004268','SRPV0832'),('5413393004275','SRPV0868'),
('5413393004282','SRPV0878'),('5413393004299','SRPV0880'),('5413393004305','SRPV0895'),
('5413393004312','SRPV0907'),('5413393004329','SRPV0910')]

def ean13_ok(c):
    if len(c)!=13 or not c.isdigit(): return False
    s=sum(int(d)*(3 if i%2 else 1) for i,d in enumerate(c[:12]))
    return (10-s%10)%10==int(c[12])

bad=[e for e,_ in PAIRS if not ean13_ok(e)]
assert not bad, f'EAN invalides: {bad}'
assert len(set(e for e,_ in PAIRS))==17 and len(set(r for _,r in PAIRS))==17, 'doublons'
print('17 EAN-13 valides (cle de controle OK), aucun doublon.\n')

for ean, ref in PAIRS:
    p=call('product.product','search_read',[[('default_code','=',ref)]],{'fields':['id','name','barcode']})
    if len(p)!=1:
        print(f'!! {ref}: {len(p)} produit(s) -> IGNORE'); continue
    p=p[0]; cur=p['barcode'] or ''
    if cur==ean:
        print(f'=  {ref} deja OK ({ean})'); continue
    dup=call('product.product','search_count',[[('barcode','=',ean),('id','!=',p['id'])]])
    if dup:
        print(f'!! {ref}: {ean} deja utilise ailleurs -> IGNORE'); continue
    tag='REMPLACE' if cur else 'AJOUT   '
    print(f'{tag} {ref} [{p["id"]}] {cur or "(vide)":>15} -> {ean}   {p["name"]}')
    if APPLY:
        call('product.product','write',[[p['id']],{'barcode':ean}])

print('\n' + ('APPLIQUE.' if APPLY else 'DRY-RUN (relancer avec --apply).'))
