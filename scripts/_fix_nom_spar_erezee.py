"""Renomme la fiche de livraison #123302 en 'Spar Erezee' (elle portait le nom
de la gerante, Nathalie Piron -> le magasin n'etait pas identifiable dans le
planning). Le contact est conserve dans le comment."""
import sys, xmlrpc.client
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})
APPLY='--apply' in sys.argv

info=call('res.partner','fields_get',[['name','comment']],{'attributes':['string','translate']})
print('name.translate =',info['name'].get('translate'))

PID=123302
cur=call('res.partner','read',[[PID]],{'fields':['name','comment','phone','email','parent_id']})[0]
print('avant :',cur['name'],'| parent',cur['parent_id'])

NEW='Spar Erezée'
note=('<p>Contact magasin : Nathalie Piron (gérante) — +32 86 47 72 82 — '
      'legribouillon@hotmail.com</p>')
comment=(cur['comment'] or '') + note if cur['comment'] else note
print('apres :',NEW)
print('comment :',note)
if APPLY:
    call('res.partner','write',[[PID],{'name':NEW,'comment':comment}])
    v=call('res.partner','read',[[PID]],{'fields':['name','comment']})[0]
    print('\nOK ->',v['name'])
else:
    print('\nDRY-RUN (--apply pour ecrire)')
