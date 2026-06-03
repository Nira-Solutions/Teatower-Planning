# -*- coding: utf-8 -*-
"""VOLET 3 - AUTOMATION : ir.cron horaire qui backfill country_id des parents Shopify
B2C sans pays (logique non-ambigue identique au backfill manuel). Reversible (active=False)."""
import xmlrpc.client, json
from datetime import datetime, timedelta
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None): return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

CODE = r'''
# [TVA-SHOPIFY] Backfill country_id parents Shopify B2C sans pays -> stoppe la double-TVA
# Perimetre STRICT Shopify : is_shopify_customer=True. Ne touche jamais B2B/GMS manuels.
# Logique non-ambigue : 1 seul pays parmi les enfants. Priorite enfant delivery > invoice.
Partner = env['res.partner']
parents = Partner.search([
    ('is_shopify_customer', '=', True),
    ('country_id', '=', False),
    ('parent_id', '=', False),
])
for p in parents:
    kids = p.child_ids.filtered(lambda c: c.country_id)
    if not kids:
        continue
    countries = set(kids.mapped('country_id').ids)
    if len(countries) != 1:
        # pays divergents -> ambigu, on laisse pour decision manuelle
        continue
    deliv = kids.filtered(lambda c: c.type == 'delivery')
    inv = kids.filtered(lambda c: c.type == 'invoice')
    src = deliv[:1] or inv[:1] or kids[:1]
    p.write({'country_id': src.country_id.id})
'''.strip()

nextcall=(datetime.now()+timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
cron_id=call('ir.cron','create',[{
    'name':'[TVA-SHOPIFY] Backfill pays parents Shopify (anti double-TVA)',
    'model_id':87,            # res.partner
    'state':'code',
    'code':CODE,
    'interval_number':1,
    'interval_type':'hours',
    'active':True,
    'nextcall':nextcall,
    'user_id':uid,
    'priority':5,
}])
print("ir.cron cree id =",cron_id)
rec=call('ir.cron','read',[[cron_id]],{'fields':['name','active','interval_number','interval_type','nextcall','state','model_id']})
print(json.dumps(rec,indent=2,default=str,ensure_ascii=False))

# Logger pour rollback
rb=json.load(open('_tva_shopify_backfill_rollback.json',encoding='utf-8'))
rb['automation']={'type':'ir.cron','id':cron_id,
    'name':'[TVA-SHOPIFY] Backfill pays parents Shopify (anti double-TVA)',
    'trigger':'periodique horaire (interval 1h)',
    'desactiver':"Parametres techniques > Automatisation > Actions planifiees : decocher 'Actif' sur le cron id=%d, OU via RPC ir.cron.write([%d],{'active':False})"%(cron_id,cron_id),
    'supprimer':"ir.cron.unlink([%d])"%cron_id}
json.dump(rb,open('_tva_shopify_backfill_rollback.json','w',encoding='utf-8'),
          ensure_ascii=False,indent=2,default=str)
print("\nRollback mis a jour avec id cron.")
