#!/usr/bin/env python3
"""Complément tagging canaux Teatower — rattrape les cas manqués par v1."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import xmlrpc.client, re

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"
TAG = {"GMS": 88, "Horeca": 84, "B2B": 85, "Shopify": 86, "Amazon": 87}
ALL_TAGS = list(TAG.values())

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None): return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

def add_tag(pids, tag_id):
    if not pids: return 0
    for i in range(0, len(pids), 200):
        call('res.partner', 'write', [pids[i:i+200], {'category_id': [(4, tag_id)]}])
    return len(pids)

HORECA_KW = ["hotel","hôtel","radisson","ibis","novotel","mercure","b&b","gîte","gite",
             "resort","restaurant","brasserie","bistro","bistrot","café","cafe","taverne",
             "auberge","lounge","rooftop","tea room","salon de thé","pizzeria","chambre",
             "domaine de","château","chateau"]
GMS_KW = ["delhaize","carrefour","spar","intermarché","intermarche","match","colruyt",
          "cora","lidl","aldi","mestdagh"," ad ","ad delhaize","affilié","affilie",
          "lambertdis","proxi delhaize","shop&go"]
HORECA_RE = re.compile("|".join(re.escape(k) for k in HORECA_KW), re.IGNORECASE)
GMS_RE = re.compile("|".join(re.escape(k) for k in GMS_KW), re.IGNORECASE)

# État avant
print("=== AVANT ===")
for name, tid in TAG.items():
    n = call('res.partner', 'search_count', [[('category_id','in',[tid])]])
    print(f"  Canal {name:10}: {n}")

# ---------- 1. Amazon via sales team ----------
print("\n=== AMAZON via crm.team ===")
teams = call('crm.team', 'search_read', [[('name','ilike','amazon')]], {'fields':['id','name']})
team_ids = [t['id'] for t in teams]
print(f"Amazon teams : {[t['name'] for t in teams]} (ids {team_ids})")
if team_ids:
    sos = call('sale.order', 'search', [[('team_id','in',team_ids),
                                          ('state','in',['sale','done','draft','sent'])]])
    print(f"SO rattachés à Amazon teams : {len(sos)}")
    if sos:
        pids = set()
        for i in range(0, len(sos), 500):
            rows = call('sale.order','read',[sos[i:i+500]],{'fields':['partner_id']})
            for r in rows:
                if r['partner_id']: pids.add(r['partner_id'][0])
        # Filtrer non-tagués
        already = set(call('res.partner','search',[[('id','in',list(pids)),('category_id','in',ALL_TAGS)]]))
        to_tag = [pid for pid in pids if pid not in already]
        n = add_tag(to_tag, TAG['Amazon'])
        print(f"  ✓ {n} partners tagués DTC Amazon")

# ---------- 2. Affiliés GMS via parent_id ----------
print("\n=== GMS via parent déjà tagué ===")
gms_parents = call('res.partner','search',[[('category_id','in',[TAG['GMS']])]])
print(f"Parents GMS : {len(gms_parents)}")
children = call('res.partner','search',[[('parent_id','in',gms_parents),
                                          ('category_id','not in',ALL_TAGS)]])
print(f"Enfants de GMS sans tag : {len(children)}")
n = add_tag(children, TAG['GMS'])
print(f"  ✓ {n} enfants tagués Canal GMS")

# ---------- 3. Relancer GMS par nom sur tous les partners non tagués ----------
print("\n=== GMS rattrapage nom (affiliés non sous parent) ===")
# Chercher 'Affilié' / GMS keywords chez partners non tagués
candidates = call('res.partner','search_read',
    [[('category_id','not in',ALL_TAGS),('active','=',True)]],
    {'fields':['id','name','parent_id'],'limit':20000})
gms_new = []
for p in candidates:
    hay = (p['name'] or '') + ' ' + (p['parent_id'][1] if p.get('parent_id') else '')
    if GMS_RE.search(hay):
        gms_new.append(p['id'])
n = add_tag(gms_new, TAG['GMS'])
print(f"  ✓ {n} partners tagués Canal GMS (nom match)")

# ---------- 4. Horeca rattrapage ----------
print("\n=== HORECA rattrapage nom ===")
horeca_new = []
for p in candidates:
    if p['id'] in gms_new: continue
    hay = (p['name'] or '') + ' ' + (p['parent_id'][1] if p.get('parent_id') else '')
    if HORECA_RE.search(hay):
        horeca_new.append(p['id'])
# refresh untagged
still_untagged = set(call('res.partner','search',[[('id','in',horeca_new),('category_id','not in',ALL_TAGS)]]))
horeca_new = [pid for pid in horeca_new if pid in still_untagged]
n = add_tag(horeca_new, TAG['Horeca'])
print(f"  ✓ {n} partners tagués Canal Horeca")

# ---------- 5. Shopify fallback particuliers avec commandes ----------
print("\n=== SHOPIFY fallback particuliers avec commandes ===")
# Chercher tous les partners avec 1+ sale_order confirmée, non tagués, is_company=False
groups = m.execute_kw(DB,uid,PWD,'sale.order','read_group',
    [[('state','in',['sale','done'])], ['partner_id'], ['partner_id']], {'limit':10000})
buyer_ids = [g['partner_id'][0] for g in groups if g['partner_id']]
# Particuliers sans tag
not_tagged = set()
for i in range(0, len(buyer_ids), 300):
    batch = buyer_ids[i:i+300]
    tg = set(call('res.partner','search',[[('id','in',batch),('category_id','in',ALL_TAGS)]]))
    not_tagged.update(pid for pid in batch if pid not in tg)
print(f"Acheteurs sans tag canal : {len(not_tagged)}")
# Classer : particuliers (is_company=False) → Shopify, entreprises → B2B
if not_tagged:
    info = call('res.partner','read',[list(not_tagged)],{'fields':['id','is_company','parent_id','name']})
    shopify_new = [p['id'] for p in info if not p['is_company']]
    b2b_new = [p['id'] for p in info if p['is_company']]
    n = add_tag(shopify_new, TAG['Shopify'])
    print(f"  ✓ {n} particuliers tagués DTC Shopify")
    n = add_tag(b2b_new, TAG['B2B'])
    print(f"  ✓ {n} entreprises tagués B2B Direct")

# État après
print("\n=== APRÈS ===")
total = 0
for name, tid in TAG.items():
    n = call('res.partner', 'search_count', [[('category_id','in',[tid])]])
    total += n
    print(f"  Canal {name:10}: {n}")

# Couverture acheteurs
tagged_buyers = 0
for i in range(0, len(buyer_ids), 300):
    tagged_buyers += call('res.partner','search_count',
        [[('id','in',buyer_ids[i:i+300]),('category_id','in',ALL_TAGS)]])
print(f"\nCouverture acheteurs (SO confirmée) : {tagged_buyers}/{len(buyer_ids)} = {100*tagged_buyers/len(buyer_ids):.1f}%")
