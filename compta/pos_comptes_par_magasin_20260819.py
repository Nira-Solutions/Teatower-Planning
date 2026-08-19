"""
Un compte de produit par magasin Teatower (POS) - 19/08/2026
-----------------------------------------------------------
Constat : les 6 pos.config partagent le meme journal et toutes les categories
produit pointent sur 700000 -> le compte de resultat n'a aucune notion de magasin.
Les autres canaux sont deja ventiles par POSITION FISCALE (FP GMS mappe
700000->700600, FP Horeca ->700300, etc.). On applique strictement le meme
pattern aux magasins : 1 FP par magasin, mapping de COMPTE uniquement,
AUCUN mapping de taxe -> la TVA reste rigoureusement inchangee.

Mecanique Odoo : a la cloture de session, pos.session._get_income_account()
applique order.fiscal_position_id.map_account() sur le compte issu de la
categorie produit. La FP posee en default_fiscal_position_id sur la pos.config
est recopiee sur chaque pos.order cree ENSUITE (les commandes deja encodees
dans les sessions ouvertes gardent fiscal_position_id=False -> 700000, elles
sont couvertes par l'OD de reclassement).

Usage : python pos_comptes_par_magasin_20260819.py [--apply]
"""
import os, sys, xmlrpc.client

URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'
USER='nicolas.raes@teatower.com'
PWD=os.environ.get('ODOO_PWD')
if not PWD: raise SystemExit("Definir ODOO_PWD")
uid=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common').authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def c(mo,me,a,k=None): return m.execute_kw(DB,uid,PWD,mo,me,a,k or {})

DRY = '--apply' not in sys.argv
print(f"MODE: {'DRY-RUN' if DRY else 'APPLY'}\n")

SRC_CODE='700000'
src=c('account.account','search_read',[[['code','=',SRC_CODE]]],{'fields':['id','code','name']})[0]

# code, libelle, FP, [pos.config ids]
MAGASINS=[
 ('700410','Ventes magasin Namur',            'Magasin Namur',    [4]),
 ('700420','Ventes magasin Liege',            'Magasin Liege',    [3,5]),
 ('700430','Ventes magasin Rocourt',          'Magasin Rocourt',  [7]),
 ('700440','Ventes magasin Waterloo',         'Magasin Waterloo', [1]),
 ('700450','Ventes pop-up & evenements',      'Magasin Pop-up',   [2]),
]

print("=== ETAPE 1 : COMPTES 7004xx ===")
acc_ids={}
for code,name,_,_ in MAGASINS:
    ex=c('account.account','search_read',[[['code','=',code]]],{'fields':['id','name']})
    if ex:
        acc_ids[code]=ex[0]['id']; print(f"  EXISTE {code} {ex[0]['name']} (id={ex[0]['id']})"); continue
    if DRY:
        print(f"  DRY    CREATE {code} {name}"); acc_ids[code]=None; continue
    aid=c('account.account','create',[{'code':code,'name':name,'account_type':'income','company_ids':[(6,0,[1])]}])
    acc_ids[code]=aid; print(f"  CREATED {code} {name} (id={aid})")

print("\n=== ETAPE 2 : POSITIONS FISCALES (mapping de compte seul, auto_apply=False) ===")
fp_ids={}
for code,name,fpname,_ in MAGASINS:
    ex=c('account.fiscal.position','search_read',[[['name','=',fpname]]],{'fields':['id']})
    if ex:
        fp_ids[fpname]=ex[0]['id']; print(f"  EXISTE FP {fpname} (id={ex[0]['id']})")
    elif DRY:
        print(f"  DRY    CREATE FP {fpname} : {SRC_CODE} -> {code}"); fp_ids[fpname]=None; continue
    else:
        fid=c('account.fiscal.position','create',[{'name':fpname,'auto_apply':False,'company_id':1}])
        fp_ids[fpname]=fid; print(f"  CREATED FP {fpname} (id={fid})")
    if DRY: continue
    fid=fp_ids[fpname]
    has=c('account.fiscal.position.account','search_read',[[['position_id','=',fid],['account_src_id','=',src['id']]]],{'fields':['id','account_dest_id']})
    if has:
        print(f"    mapping deja present -> {has[0]['account_dest_id'][1]}")
    else:
        c('account.fiscal.position.account','create',[{'position_id':fid,'account_src_id':src['id'],'account_dest_id':acc_ids[code]}])
        print(f"    mapping {SRC_CODE} -> {code} cree")

print("\n=== ETAPE 3 : BRANCHEMENT SUR LES POS.CONFIG ===")
for code,name,fpname,cfgs in MAGASINS:
    for cid in cfgs:
        cfg=c('pos.config','read',[[cid]],{'fields':['name','default_fiscal_position_id','fiscal_position_ids']})[0]
        if DRY:
            print(f"  DRY    #{cid} {cfg['name'][:16]:16} default_fiscal_position_id -> {fpname} (actuel={cfg['default_fiscal_position_id']})")
            continue
        fid=fp_ids[fpname]
        try:
            c('pos.config','write',[[cid],{'fiscal_position_ids':[(6,0,[fid])],'default_fiscal_position_id':fid}])
            print(f"  OK     #{cid} {cfg['name'][:16]:16} -> FP {fpname} (compte {code})")
        except Exception as e:
            print(f"  ERREUR #{cid} {cfg['name'][:16]:16} : {str(e)[:160]}")
print("\nTermine.")
