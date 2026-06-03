# -*- coding: utf-8 -*-
"""TEST VALIDATION : creer un devis DRAFT temporaire sur un parent backfille (BE/FR/DE),
lire la FP auto-calculee (fiscal_position_id), puis SUPPRIMER le draft. Un draft non
confirme n'a aucun impact compta/stock. 100% reversible."""
import xmlrpc.client, json
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

dry=json.load(open('_tva_shopify_dryrun.json',encoding='utf-8'))
samples={}
for t in dry['to_treat']:
    if t['country_name'] not in samples: samples[t['country_name']]=t
picks=[samples[k] for k in ('Belgium','France','Germany') if k in samples]

EXPECT={'Belgium':'EU B2C','France':'OSS B2C France','Germany':'OSS B2C Allemagne'}
results=[]
for t in picks:
    pid=t['parent_id']
    # Creer devis draft : la FP doit etre auto-appliquee via onchange partner
    oid=call('sale.order','create',[{'partner_id':pid}])
    so=call('sale.order','read',[[oid]],{'fields':['name','fiscal_position_id','state','partner_id']})[0]
    fp=so['fiscal_position_id']
    fpname=fp[1] if fp else 'AUCUNE'
    exp=EXPECT.get(t['country_name'])
    ok = (fpname==exp)
    results.append({'parent_id':pid,'name':t['name'],'country':t['country_name'],
                    'fp_obtenue':fpname,'fp_attendue':exp,'OK':ok,'draft_state':so['state']})
    print(f"  {t['country_name']:10} parent#{pid} -> FP='{fpname}' (attendu '{exp}') {'OK' if ok else 'KO!!'}")
    # SUPPRIMER le draft de test
    call('sale.order','unlink',[[oid]])
    print(f"      devis draft {so['name']} supprime.")

json.dump(results,open('_tva_shopify_validate.json','w',encoding='utf-8'),
          ensure_ascii=False,indent=2,default=str)
allok=all(r['OK'] for r in results)
print(f"\n=== VALIDATION {'TOUTES OK' if allok else 'ECHEC sur au moins 1'} ===")
