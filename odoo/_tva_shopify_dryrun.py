# -*- coding: utf-8 -*-
"""VOLET 1 - DRY-RUN : identifier les parents Shopify sans country_id ayant un enfant (delivery/invoice) AVEC pays.
Priorite enfant 'delivery' sinon 'invoice'. Pays enfants divergents => AMBIGU, non traite.
Produit la liste complete dans _tva_shopify_dryrun.json. AUCUNE ECRITURE."""
import xmlrpc.client, json
from collections import defaultdict
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

# 1. Parents Shopify sans pays : is_shopify_customer=True, country_id=False, parent_id=False (= sommet B2C)
parents=call('res.partner','search_read',
    [[['is_shopify_customer','=',True],['country_id','=',False],['parent_id','=',False]]],
    {'fields':['id','name','child_ids','type','company_type','property_account_position_id','customer_rank']})
print(f"Parents Shopify sans pays (parent_id=False) : {len(parents)}")

# Recolter tous les child_ids pour un read groupe
all_kids=set()
for p in parents: all_kids.update(p.get('child_ids') or [])
kids_data={}
all_kids=list(all_kids)
CH=300
for i in range(0,len(all_kids),CH):
    for k in call('res.partner','read',[all_kids[i:i+CH]],
        {'fields':['id','name','type','country_id']}):
        kids_data[k['id']]=k

to_treat=[]      # non ambigus : on recopiera le pays
ambiguous=[]     # pays enfants divergents
no_child_country=[]  # parent sans aucun enfant avec pays

for p in parents:
    kids=[kids_data[c] for c in (p.get('child_ids') or []) if c in kids_data]
    # enfants avec pays
    with_country=[k for k in kids if k['country_id']]
    if not with_country:
        no_child_country.append({'parent_id':p['id'],'name':p['name'],
            'nb_children':len(kids)})
        continue
    # pays distincts presents
    countries=set(k['country_id'][0] for k in with_country)
    if len(countries)>1:
        ambiguous.append({'parent_id':p['id'],'name':p['name'],
            'countries':sorted({(k['country_id'][0],k['country_id'][1]) for k in with_country},key=lambda x:x[0]),
            'children':[{'id':k['id'],'type':k['type'],'country':k['country_id'][1]} for k in with_country]})
        continue
    # non ambigu : 1 seul pays. Priorite delivery>invoice>autre pour la source
    deliv=[k for k in with_country if k['type']=='delivery']
    inv=[k for k in with_country if k['type']=='invoice']
    src = deliv[0] if deliv else (inv[0] if inv else with_country[0])
    to_treat.append({'parent_id':p['id'],'name':p['name'],
        'country_id':src['country_id'][0],'country_name':src['country_id'][1],
        'source_child_id':src['id'],'source_child_type':src['type'],
        'current_fp':p['property_account_position_id'] or False})

out={'summary':{
        'parents_shopify_sans_pays_total':len(parents),
        'a_traiter':len(to_treat),
        'ambigus_pays_divergents':len(ambiguous),
        'sans_enfant_avec_pays':len(no_child_country)},
     'to_treat':to_treat,'ambiguous':ambiguous,'no_child_country':no_child_country}

# repartition par pays a traiter
bypays=defaultdict(int)
for t in to_treat: bypays[t['country_name']]+=1
out['summary']['repartition_pays_a_traiter']=dict(sorted(bypays.items(),key=lambda x:-x[1]))

with open('_tva_shopify_dryrun.json','w',encoding='utf-8') as f:
    json.dump(out,f,ensure_ascii=False,indent=2,default=str)

print("\n=== RESUME DRY-RUN ===")
print(json.dumps(out['summary'],indent=2,ensure_ascii=False))
print(f"\nFichier: _tva_shopify_dryrun.json")
if ambiguous:
    print(f"\n!!! {len(ambiguous)} AMBIGUS (pays divergents) - NON traites :")
    for a in ambiguous: print(f"  #{a['parent_id']} {a['name']} -> {[c[1] for c in a['countries']]}")
