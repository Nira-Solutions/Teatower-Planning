"""
GMS Top 9 Best-Sellers — lecture seule Odoo
Lancer : python data-bi/gms_top9.py
"""
import xmlrpc.client
from collections import defaultdict
from datetime import datetime, date

URL = "https://tea-tree.odoo.com"
DB  = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD  = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
print(f"Connecte uid={uid}")
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

# ─── ETAPE 1 : Segmentation GMS ─────────────────────────────────────────────
print("\n=== 1. TAGS res.partner.category ===")
tags = call('res.partner.category', 'search_read', [[]], {
    'fields': ['id', 'name'], 'limit': 100
})
for t in tags:
    print(f"  id={t['id']}  name={t['name']}")

print("\n=== 2. Equipes de vente (crm.team) ===")
teams = call('crm.team', 'search_read', [[]], {
    'fields': ['id', 'name'], 'limit': 50
})
for t in teams:
    print(f"  id={t['id']}  name={t['name']}")

print("\n=== 3. Propriete analytic / canal sur quelques partenaires Delhaize ===")
# Chercher quelques clients dont le nom contient GMS keywords
gms_keywords = ['delhaize', 'carrefour', 'intermarche', 'colruyt', 'match', 'spar', 'ad delhaize']
partner_ids_sample = []
for kw in ['delhaize', 'carrefour', 'intermarche']:
    res = call('res.partner', 'search_read',
               [[['name', 'ilike', kw], ['customer_rank', '>', 0]]],
               {'fields': ['id', 'name', 'category_id'], 'limit': 5})
    for r in res:
        print(f"  {r['id']}  {r['name']}  tags={r['category_id']}")
        partner_ids_sample.append(r['id'])

# ─── ETAPE 2 : Identifier la catégorie/tag GMS exact ────────────────────────
# On cherche un tag contenant 'GMS' ou 'grande surface'
gms_tag_ids = []
for t in tags:
    if any(k in t['name'].lower() for k in ['gms', 'grande surface', 'supermarche', 'supermarket', 'retail', 'enseigne']):
        gms_tag_ids.append(t['id'])
        print(f"\n  >> TAG GMS candidat : id={t['id']} name={t['name']}")

# ─── ETAPE 3 : Identifier tous les partenaires GMS ──────────────────────────
# Stratégie A : par tag si trouvé
# Stratégie B : par nom (keywords enseignes) — fallback fiable
print("\n=== 4. Construction liste partenaires GMS ===")

# Stratégie A — tag
gms_partners_by_tag = []
if gms_tag_ids:
    gms_partners_by_tag = call('res.partner', 'search_read',
        [[['category_id', 'in', gms_tag_ids], ['customer_rank', '>', 0]]],
        {'fields': ['id', 'name', 'category_id'], 'limit': 500})
    print(f"  Strategie A (tag) : {len(gms_partners_by_tag)} partenaires")

# Stratégie B — par nom enseigne (noms contenant les mots clés)
gms_name_domain = ['|'] * 6 + [
    ['name', 'ilike', 'delhaize'],
    ['name', 'ilike', 'carrefour'],
    ['name', 'ilike', 'intermarche'],
    ['name', 'ilike', 'intermarché'],
    ['name', 'ilike', 'match'],
    ['name', 'ilike', 'colruyt'],
    ['name', 'ilike', 'spar'],
]
# rebuild proprement
domain_name = [
    '|','|','|','|','|','|',
    ['name', 'ilike', 'delhaize'],
    ['name', 'ilike', 'carrefour'],
    ['name', 'ilike', 'intermarche'],
    ['name', 'ilike', 'intermarché'],
    ['name', 'ilike', 'spar'],
    ['name', 'ilike', 'colruyt'],
    ['name', 'ilike', 'match'],
]
gms_partners_by_name = call('res.partner', 'search_read',
    [domain_name + [['customer_rank', '>', 0]]],
    {'fields': ['id', 'name', 'category_id'], 'limit': 500})
print(f"  Strategie B (nom enseigne) : {len(gms_partners_by_name)} partenaires")
for p in sorted(gms_partners_by_name, key=lambda x: x['name']):
    print(f"    {p['id']}  {p['name']}  tags={p['category_id']}")

# Segmentation RETENUE = tag officiel canal (Canal GMS id=88 + GMS id=27).
# La strategie nom-enseigne sert UNIQUEMENT de controle (faux positifs hors canal).
all_gms_ids = set(p['id'] for p in gms_partners_by_tag)
name_ids = set(p['id'] for p in gms_partners_by_name)
extra_name_only = name_ids - all_gms_ids
print(f"\n  >> Partenaires GMS retenus (tag canal) : {len(all_gms_ids)}")
print(f"  (controle) noms d'enseigne PAS dans le tag Canal GMS : {len(extra_name_only)} "
      f"(exclus du classement - hors canal GMS officiel)")

# ─── ETAPE 4 : Commandes GMS 12 mois glissants ──────────────────────────────
date_from = "2025-05-27"
date_to   = "2026-05-27"
print(f"\n=== 5. Commandes GMS [{date_from} → {date_to}] ===")

gms_partner_list = list(all_gms_ids)

orders = call('sale.order', 'search_read',
    [[
        ['partner_id', 'in', gms_partner_list],
        ['state', 'in', ['sale', 'done']],
        ['date_order', '>=', date_from],
        ['date_order', '<=', date_to],
    ]],
    {'fields': ['id', 'name', 'partner_id', 'date_order', 'amount_untaxed'], 'limit': 2000})

order_ids = [o['id'] for o in orders]
print(f"  {len(orders)} commandes trouvees, {len(order_ids)} ids")

if not order_ids:
    print("  AUCUNE commande GMS — verifier la segmentation")
    exit()

# Recap CA total
total_ca = sum(o['amount_untaxed'] for o in orders)
print(f"  CA total brut commandes GMS : {total_ca:,.2f} EUR HT")

# ─── ETAPE 5 : Lines de commande ────────────────────────────────────────────
print("\n=== 6. Lines de commande GMS ===")

# Chunker par 200 pour ne pas exploser xmlrpc
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

all_lines = []
for chunk in chunks(order_ids, 200):
    lines = call('sale.order.line', 'search_read',
        [[['order_id', 'in', chunk]]],
        {'fields': ['id', 'order_id', 'product_id', 'product_uom_qty',
                    'price_subtotal', 'price_unit', 'discount',
                    'product_template_id', 'name'], 'limit': 5000})
    all_lines.extend(lines)

print(f"  {len(all_lines)} lignes de commande recuperees")

# ─── ETAPE 6 : Récupérer les default_code (SKU) ─────────────────────────────
# On récupère les product.template pour avoir ref + categ
template_ids = list({l['product_template_id'][0] for l in all_lines if l['product_template_id']})
print(f"  {len(template_ids)} templates distincts")

templates_raw = []
for chunk in chunks(template_ids, 200):
    t = call('product.template', 'search_read',
        [[['id', 'in', chunk]]],
        {'fields': ['id', 'name', 'default_code', 'categ_id', 'type'], 'limit': 1000})
    templates_raw.extend(t)

tmpl_map = {t['id']: t for t in templates_raw}

# ─── ETAPE 7 : Filtrage lignes non-produit ──────────────────────────────────
# Exclusions : transport, frais, PLV/displays (catégorie ou nom contient ces mots)
EXCLUDE_KEYWORDS = ['transport', 'frais', 'livraison', 'plv', 'display',
                    'présentoir', 'presentoir', 'service', 'remise']
EXCLUDE_CATEG_KEYWORDS = ['service', 'transport', 'frais', 'display', 'plv']

excluded = []
included = []

for line in all_lines:
    if not line['product_template_id']:
        excluded.append(('no_template', line.get('name', '?')))
        continue
    tid = line['product_template_id'][0]
    tmpl = tmpl_map.get(tid)
    if not tmpl:
        excluded.append(('tmpl_not_found', tid))
        continue

    name_lower = (tmpl['name'] or '').lower()
    code_lower = (tmpl['default_code'] or '').lower()
    categ_lower = (tmpl['categ_id'][1] if tmpl['categ_id'] else '').lower()

    if any(k in name_lower for k in EXCLUDE_KEYWORDS):
        excluded.append(('name_keyword', tmpl['name']))
        continue
    if any(k in code_lower for k in EXCLUDE_KEYWORDS):
        excluded.append(('code_keyword', tmpl['default_code']))
        continue
    if any(k in categ_lower for k in EXCLUDE_CATEG_KEYWORDS):
        excluded.append(('categ_keyword', categ_lower))
        continue
    # Exclusions sur demande : thes glaces (GI0) + emballages/SRP (EM)
    if code_lower.startswith('gi0') or code_lower.startswith('em'):
        excluded.append(('prefix_gi0_em', tmpl['default_code']))
        continue

    included.append(line)

print(f"  Lignes incluses : {len(included)}")
print(f"  Lignes exclues  : {len(excluded)}")
# Afficher les exclusions distinctes
excl_sample = {}
for reason, val in excluded:
    excl_sample.setdefault(reason, set()).add(str(val))
for r, vals in excl_sample.items():
    print(f"    Exclusion [{r}] : {list(vals)[:10]}")

# ─── ETAPE 8 : Agrégation par template ──────────────────────────────────────
agg = defaultdict(lambda: {'qty': 0.0, 'ca': 0.0, 'clients': set(), 'orders': set()})

for line in included:
    tid = line['product_template_id'][0]
    order_id = line['order_id'][0]
    # Retrouver le partner via order
    agg[tid]['qty'] += line['product_uom_qty']
    agg[tid]['ca']  += line['price_subtotal']
    agg[tid]['orders'].add(order_id)

# Mapper order_id -> partner_id
order_partner = {o['id']: o['partner_id'][0] for o in orders}
for line in included:
    tid = line['product_template_id'][0]
    oid = line['order_id'][0]
    pid = order_partner.get(oid)
    if pid:
        agg[tid]['clients'].add(pid)

# ─── ETAPE 9 : Tri et top 9 ─────────────────────────────────────────────────
ranked = sorted(agg.items(), key=lambda x: x[1]['qty'], reverse=True)

print("\n" + "="*90)
print(f"TOP 9 BEST-SELLERS GMS — Quantite — {date_from} au {date_to}")
print("="*90)
header = f"{'Rg':>3}  {'SKU':<15}  {'Nom produit':<45}  {'Qty':>8}  {'CA HT (€)':>12}  {'Nb clients':>10}"
print(header)
print("-"*90)

for rank, (tid, data) in enumerate(ranked[:9], 1):
    tmpl = tmpl_map.get(tid, {})
    sku  = tmpl.get('default_code') or '—'
    name = (tmpl.get('name') or '?')[:45]
    qty  = data['qty']
    ca   = data['ca']
    nb_clients = len(data['clients'])
    print(f"{rank:>3}  {sku:<15}  {name:<45}  {qty:>8.0f}  {ca:>12,.2f}  {nb_clients:>10}")

print("-"*90)
print(f"\n  Partenaires GMS couverts  : {len(all_gms_ids)}")
print(f"  Commandes GMS             : {len(orders)}")
print(f"  Periode                   : {date_from} -> {date_to}")
print(f"  CA total GMS (cmds val.)  : {total_ca:,.2f} EUR HT")
print(f"  Segmentation retenue      : union tag GMS ({len(gms_tag_ids)} tag(s)) + nom enseigne (Delhaize/Carrefour/Intermarche/Spar/Colruyt/Match)")

# Bonus : top 20 pour info
print("\n--- TOP 20 complet (reference) ---")
for rank, (tid, data) in enumerate(ranked[:20], 1):
    tmpl = tmpl_map.get(tid, {})
    sku  = tmpl.get('default_code') or '—'
    name = (tmpl.get('name') or '?')[:45]
    print(f"  {rank:>2}. {sku:<15}  {name:<45}  qty={data['qty']:>8.0f}  ca={data['ca']:>10,.2f}")
