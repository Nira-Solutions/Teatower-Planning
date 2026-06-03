# -*- coding: utf-8 -*-
"""VOLET 2 - BACKFILL : ecrire country_id sur les 167 parents Shopify non-ambigus.
Avant chaque write, re-verif que country_id est bien False (securite). Rollback complet ecrit."""
import xmlrpc.client, json
from datetime import datetime
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

dry=json.load(open('_tva_shopify_dryrun.json',encoding='utf-8'))
to_treat=dry['to_treat']
ids=[t['parent_id'] for t in to_treat]

# Securite : re-lire l'etat actuel country_id de tous les parents cibles
cur={p['id']:p for p in call('res.partner','read',[ids],{'fields':['country_id','is_shopify_customer','parent_id']})}

rollback={'created_at':datetime.now().isoformat(),
          'description':'Backfill country_id parents Shopify B2C sans pays (correction double-TVA). Pour annuler: remettre country_id=False sur ces ids.',
          'entries':[]}
done=0; skipped=[]
for t in to_treat:
    pid=t['parent_id']; c=cur.get(pid)
    # garde-fous : doit etre Shopify, sans pays, sans parent
    if not c or c['country_id'] or not c['is_shopify_customer'] or c['parent_id']:
        skipped.append({'parent_id':pid,'reason':'etat change depuis dry-run',
                        'now':c['country_id'] if c else 'introuvable'})
        continue
    call('res.partner','write',[[pid],{'country_id':t['country_id']}])
    rollback['entries'].append({'parent_id':pid,'name':t['name'],
        'country_before':False,'country_after':t['country_id'],
        'country_name':t['country_name'],'source_child_id':t['source_child_id'],
        'source_child_type':t['source_child_type']})
    done+=1

rollback['count']=done
rollback['skipped']=skipped
rollback['ambiguous_not_treated']=dry['ambiguous']
json.dump(rollback,open('_tva_shopify_backfill_rollback.json','w',encoding='utf-8'),
          ensure_ascii=False,indent=2,default=str)

print(f"=== BACKFILL TERMINE ===")
print(f"  Parents backfilles : {done}")
print(f"  Skipped (etat change) : {len(skipped)}")
print(f"  Ambigus non traites : {len(dry['ambiguous'])}")
print(f"  Rollback : _tva_shopify_backfill_rollback.json")
if skipped:
    for s in skipped: print("   SKIP",s)
