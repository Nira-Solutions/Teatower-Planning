"""
Active reellement les positions fiscales "Magasin" sur les pos.config.
-----------------------------------------------------------------------
Diagnostic du 31/08/2026 : les FP #36-40 etaient bien posees en
`default_fiscal_position_id` depuis le 19/08, mais :
    - `fiscal_position_ids`  = []      sur les 6 configs
    - `tax_regime_selection` = False   sur les 6 configs
Le frontend POS ne charge que les FP listees dans `fiscal_position_ids` : la
default n'etant pas dedans, elle n'est jamais recopiee sur la commande.
Resultat : 1.288 pos.order d'aout avec fiscal_position_id VIDE, donc
pos.session._get_income_account() n'applique aucun map_account() et tout le CA
magasin retombe en 700000.

Ce script ajoute la FP par defaut dans la liste autorisee de chaque config.
Sans effet fiscal : les FP "Magasin" ont un mapping de COMPTE seul, zero taxe.

Prend effet a la PROCHAINE ouverture de session (le frontend charge sa config
a l'ouverture) -> controler le lendemain avec --check.

Usage : python pos_fp_magasins_activation.py [--apply] [--check]
"""
import os, sys, xmlrpc.client
from collections import defaultdict

URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'
PWD=os.environ.get('ODOO_PWD')
if not PWD: raise SystemExit("Definir ODOO_PWD")
uid=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common').authenticate(DB,'nicolas.raes@teatower.com',PWD,{})
m=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def c(mo,me,a,k=None): return m.execute_kw(DB,uid,PWD,mo,me,a,k or {})

if '--check' in sys.argv:
    o=c('pos.order','search_read',[[['date_order','>=',sys.argv[sys.argv.index('--check')+1]
        if len(sys.argv)>sys.argv.index('--check')+1 and not sys.argv[sys.argv.index('--check')+1].startswith('-')
        else '2026-09-01'],['state','in',['paid','done','invoiced']]]],
        {'fields':['config_id','fiscal_position_id']})
    agg=defaultdict(int)
    for x in o: agg[(x['config_id'][1], x['fiscal_position_id'][1] if x['fiscal_position_id'] else '*** AUCUNE ***')]+=1
    for k,v in sorted(agg.items()): print("  %-14s %-24s %5d commandes"%(k[0],k[1],v))
    raise SystemExit(0)

DRY = '--apply' not in sys.argv
print(f"MODE: {'DRY-RUN' if DRY else 'APPLY'}\n")
cfgs=c('pos.config','search_read',[[]],
    {'fields':['name','default_fiscal_position_id','fiscal_position_ids','tax_regime_selection']})
for x in cfgs:
    fp=x['default_fiscal_position_id']
    if not fp:
        print(f"  cfg#{x['id']:<2} {x['name']:<14} pas de FP par defaut -> ignore"); continue
    if fp[0] in x['fiscal_position_ids'] and x['tax_regime_selection']:
        print(f"  cfg#{x['id']:<2} {x['name']:<14} deja OK ({fp[1]})"); continue
    print(f"  cfg#{x['id']:<2} {x['name']:<14} {fp[1]:<18} "
          f"liste={x['fiscal_position_ids']} regime={x['tax_regime_selection']} -> a corriger")
    if not DRY:
        c('pos.config','write',[[x['id']],
          {'tax_regime_selection':True,'fiscal_position_ids':[(6,0,[fp[0]])]}])
if DRY:
    print("\nDRY : rien ecrit. Relancer avec --apply.")
else:
    print("\nEcrit. Prend effet a la prochaine OUVERTURE de session.")
    print("Controle le lendemain :  python pos_fp_magasins_activation.py --check 2026-09-01")
