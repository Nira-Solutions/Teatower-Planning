# -*- coding: utf-8 -*-
"""Lire les FP auto_apply pour reproduire la logique de matching Odoo et valider que
BE->EU B2C, FR->OSS FR, DE->OSS DE. Non destructif."""
import xmlrpc.client, json
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

fps=call('account.fiscal.position','search_read',
    [[['auto_apply','=',True]]],
    {'fields':['id','name','auto_apply','vat_required','country_id','country_group_id',
               'state_ids','zip_from','zip_to','sequence','company_id']})
print(f"FP auto_apply : {len(fps)}")
for f in sorted(fps,key=lambda x:(x.get('sequence') or 0, x['id'])):
    print(f"  id={f['id']:3} seq={f.get('sequence')} vat_req={f['vat_required']} "
          f"country={f['country_id']} group={f['country_group_id']} : {f['name']}")
json.dump(fps,open('_tva_shopify_fpmap.json','w',encoding='utf-8'),ensure_ascii=False,indent=2,default=str)

# Reproduction logique Odoo (account.fiscal.position._get_fiscal_position):
# filtre auto_apply, vat_required selon presence vat partner, puis prefere
# country_id exact, sinon country_group, trie par sequence/specificite.
# Pour B2C (vat=False) -> vat_required doit etre False.
print("\n=== Simulation matching B2C (vat=False) ===")
def match(country_id, has_vat=False):
    cand=[]
    for f in fps:
        if f['vat_required'] and not has_vat: continue
        cid=f['country_id'][0] if f['country_id'] else None
        # country exact
        if cid==country_id:
            cand.append((0,f.get('sequence') or 0,f['id'],f['name']))
        elif not cid and f['country_group_id']:
            cand.append((1,f.get('sequence') or 0,f['id'],f['name']))  # group resolu cote Odoo
    cand.sort()
    return cand
# BE=20, FR=76, DE=57 (ids pays Odoo standard) - on verifie via read country
for code,cid in [('BE',20)]:
    pass
