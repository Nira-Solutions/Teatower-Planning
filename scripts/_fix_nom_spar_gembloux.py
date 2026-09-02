"""Renomme #123297 en 'Spar Gembloux' (portait le nom du gerant Pascal Gilson).
Le contact est conserve dans le comment, apres le tag [REGLE:] existant."""
import sys, xmlrpc.client
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})
APPLY='--apply' in sys.argv
PID=123297; NEW='Spar Gembloux'
cur=call('res.partner','read',[[PID]],{'fields':['name','comment']})[0]
note='<p>Contact magasin : Pascal Gilson (gérant) — +32 81 61 63 14 — spar.gembloux.rpcg@gmail.com</p>'
comment=(cur['comment'] or '')+note
print(f"{cur['name']!r} -> {NEW!r}")
print('comment +=',note)
if APPLY:
    call('res.partner','write',[[PID],{'name':NEW,'comment':comment}])
    print('OK ->',call('res.partner','read',[[PID]],{'fields':['name']})[0]['name'])
else: print('DRY-RUN')
