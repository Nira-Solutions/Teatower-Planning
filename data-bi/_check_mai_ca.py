"""
Script Data-BI : CA mai 2026 par canal — version complete
Perimetre : 01/05/2026 -> 31/05/2026 (mois clos)
Source : Odoo XML-RPC lecture seule
KPI#ca-canal-2026-06-01
"""
import xmlrpc.client
from collections import defaultdict

URL = 'https://tea-tree.odoo.com'; DB = 'tsc-be-tea-tree-main-18515272'
USER = 'nicolas.raes@teatower.com'; PWD = 'Teatower123'
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

def call(m, meth, args, kw=None):
    return models.execute_kw(DB, uid, PWD, m, meth, args, kw or {})

GMS_TAGS    = {88, 27}
HORECA_TAGS = {84, 26}
B2B_TAGS    = {85}

# ────────────────────────────────────────────────────────────────
# 1. Charger les factures d'une periode
# ────────────────────────────────────────────────────────────────
def load_invoices(date_from, date_to, label=""):
    inv = call('account.move', 'search_read',
        [[('move_type', 'in', ['out_invoice', 'out_refund']),
          ('state', '=', 'posted'),
          ('invoice_date', '>=', date_from),
          ('invoice_date', '<=', date_to)]],
        {'fields': ['name','invoice_date','amount_untaxed','move_type',
                    'partner_id','journal_id','invoice_origin'], 'limit': 3000})
    print(f"[{label}] {len(inv)} factures/avoirs chargees")
    return inv

# ────────────────────────────────────────────────────────────────
# 2. Charger les tags partenaires (par batch de 100)
# ────────────────────────────────────────────────────────────────
def load_partner_tags(invoices):
    pids = list(set(i['partner_id'][0] for i in invoices if i['partner_id']))
    tags = {}
    for i in range(0, len(pids), 100):
        chunk = pids[i:i+100]
        ps = call('res.partner', 'read', [chunk], {'fields': ['id','name','category_id']})
        for p in ps:
            raw = p['category_id']
            if raw and isinstance(raw[0], (list, tuple)):
                cats = [c[0] for c in raw]
            else:
                cats = list(raw) if raw else []
            tags[p['id']] = {'name': p['name'], 'cats': cats}
    return tags

# ────────────────────────────────────────────────────────────────
# 3. Decouvrir les journaux (pour identifier POS, Shopify, etc.)
# ────────────────────────────────────────────────────────────────
print("\n=== JOURNAUX DISPONIBLES ===")
journals = call('account.journal', 'search_read',
    [[('type', 'in', ['sale', 'general'])]],
    {'fields': ['id', 'name', 'type']})
for j in journals:
    print(f"  id={j['id']:3d}  type={j['type']:8s}  name={j['name']}")

# On va identifier les IDs journaux POS, Shopify
# POS journals : nom contient "Point of Sale" ou "POS" ou "Caisse"
# Shopify : nom contient "Shopify"
pos_journal_ids = set()
shopify_journal_ids = set()
amazon_journal_ids = set()
for j in journals:
    n = j['name'].lower()
    if 'point of sale' in n or 'pos' in n or 'caisse' in n:
        pos_journal_ids.add(j['id'])
        print(f"  -> POS journal: {j['id']} {j['name']}")
    if 'shopify' in n:
        shopify_journal_ids.add(j['id'])
        print(f"  -> Shopify journal: {j['id']} {j['name']}")
    if 'amazon' in n or 'fba' in n:
        amazon_journal_ids.add(j['id'])
        print(f"  -> Amazon journal: {j['id']} {j['name']}")

# ────────────────────────────────────────────────────────────────
# 4. Classifier une facture
# ────────────────────────────────────────────────────────────────
def classify(inv, ptags):
    if not inv['partner_id']:
        return 'Autres'
    pid = inv['partner_id'][0]
    pname = inv['partner_id'][1] if isinstance(inv['partner_id'], (list,tuple)) else ''
    cats = ptags.get(pid, {}).get('cats', [])
    cats_set = set(cats)
    jid = inv['journal_id'][0] if inv['journal_id'] else None

    # Override journal POS
    if jid and jid in pos_journal_ids:
        return 'POS'
    # Override journal Shopify
    if jid and jid in shopify_journal_ids:
        return 'Shopify'
    # Override journal Amazon
    if jid and jid in amazon_journal_ids:
        return 'Amazon'

    # Origin Shopify (origin contient "Shopify" ou "#")
    origin = (inv.get('invoice_origin') or '').lower()
    if 'shopify' in origin:
        return 'Shopify'
    if 'amazon' in origin or 'fba' in origin:
        return 'Amazon'

    # Tags canal
    if cats_set & GMS_TAGS:
        return 'GMS'
    if cats_set & HORECA_TAGS:
        return 'Horeca'
    if cats_set & B2B_TAGS:
        return 'B2B'

    # Override manuel par nom partenaire connu GMS
    raw_pn = ptags.get(pid, {}).get('name', pname)
    pn = (raw_pn or '').lower() if isinstance(raw_pn, str) else ''
    gms_names = ['delhaize','carrefour','intermarche','intermadis','boisdis','newpharma',
                 'colruyt','ad delhaize','spar','match','cora','louis delhaize','proxy delhaize',
                 'barthe','carrefour market','hypermarche','supermarche']
    horeca_names = ['cafe','cafes','brasserie','restaurant','hotel','horeca','catering',
                    'maziers','delahaut','ventuno','preko','cafermi','radisson','bar ']
    b2b_names = ['vilna gaon','moulins burette','europadrinks','corica','teatower marketing',
                 'epicerie','the art','tea','spice','boutique','reseller','distributeur']
    if any(x in pn for x in gms_names):
        return 'GMS'
    if any(x in pn for x in horeca_names):
        return 'Horeca'
    if any(x in pn for x in b2b_names):
        return 'B2B'

    return 'Autres'

# ────────────────────────────────────────────────────────────────
# 5. Ventiler un ensemble de factures
# ────────────────────────────────────────────────────────────────
def ventiler(invoices, ptags):
    ca = defaultdict(float)
    nb_inv = defaultdict(int)
    clients = defaultdict(set)
    avoirs = defaultdict(float)
    top_clients = defaultdict(lambda: defaultdict(float))  # canal -> pid -> montant

    for inv in invoices:
        canal = classify(inv, ptags)
        sign = -1 if inv['move_type'] == 'out_refund' else 1
        amt = inv['amount_untaxed'] * sign
        ca[canal] += amt
        nb_inv[canal] += 1
        if inv['partner_id']:
            pid = inv['partner_id'][0]
            clients[canal].add(pid)
            top_clients[canal][pid] += amt
        if inv['move_type'] == 'out_refund':
            avoirs[canal] += inv['amount_untaxed']  # montant positif de l'avoir

    return ca, nb_inv, clients, avoirs, top_clients

# ────────────────────────────────────────────────────────────────
# 6. Charger et ventiler MAI 2026
# ────────────────────────────────────────────────────────────────
print("\n=== MAI 2026 ===")
inv_mai26 = load_invoices('2026-05-01', '2026-05-31', 'MAI 2026')
ptags_mai26 = load_partner_tags(inv_mai26)
ca26, nb26, cli26, av26, top26 = ventiler(inv_mai26, ptags_mai26)

CANAUX = ['GMS', 'B2B', 'Horeca', 'POS', 'Shopify', 'Amazon', 'Autres']
print("\n--- CA MAI 2026 par canal ---")
total_mai26 = 0
for c in CANAUX:
    v = ca26.get(c, 0)
    total_mai26 += v
    print(f"  {c:20s}: {v:>10.2f} EUR  |  {nb26.get(c,0):>3d} factures  |  {len(cli26.get(c,set())):>3d} clients")
print(f"  {'TOTAL':20s}: {total_mai26:>10.2f} EUR")
print(f"\nPerimetre 3 canaux (GMS+B2B+Horeca): {ca26.get('GMS',0)+ca26.get('B2B',0)+ca26.get('Horeca',0):>10.2f} EUR")
print(f"Avoirs par canal:")
for c in CANAUX:
    if av26.get(c, 0) > 0:
        print(f"  {c}: {av26[c]:.2f} EUR avoir")

# ────────────────────────────────────────────────────────────────
# 7. Top 5 clients par canal (GMS, Horeca, B2B)
# ────────────────────────────────────────────────────────────────
print("\n--- TOP 5 CLIENTS MAI 2026 ---")
for canal in ['GMS', 'Horeca', 'B2B']:
    tc = top26.get(canal, {})
    sorted_clients = sorted(tc.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\n{canal}:")
    for pid, amt in sorted_clients:
        pname = ptags_mai26.get(pid, {}).get('name', f'Partner#{pid}')
        print(f"  {pname:40s}  {amt:>10.2f} EUR")

# ────────────────────────────────────────────────────────────────
# 8. AVRIL 2026 reel (pour comparaison M-1)
# ────────────────────────────────────────────────────────────────
print("\n=== AVRIL 2026 (reel clos) ===")
inv_avr26 = load_invoices('2026-04-01', '2026-04-30', 'AVRIL 2026')
ptags_avr26 = load_partner_tags(inv_avr26)
ca_a26, nb_a26, cli_a26, av_a26, top_a26 = ventiler(inv_avr26, ptags_avr26)

print("\n--- CA AVRIL 2026 par canal ---")
total_avr26 = 0
for c in CANAUX:
    v = ca_a26.get(c, 0)
    total_avr26 += v
    print(f"  {c:20s}: {v:>10.2f} EUR  |  {nb_a26.get(c,0):>3d} factures")
print(f"  {'TOTAL':20s}: {total_avr26:>10.2f} EUR")

# ────────────────────────────────────────────────────────────────
# 9. MAI 2025 reel (pour comparaison A-1)
# ────────────────────────────────────────────────────────────────
print("\n=== MAI 2025 (reel clos) ===")
inv_mai25 = load_invoices('2025-05-01', '2025-05-31', 'MAI 2025')
ptags_mai25 = load_partner_tags(inv_mai25)
ca25, nb25, cli25, av25, top25 = ventiler(inv_mai25, ptags_mai25)

print("\n--- CA MAI 2025 par canal ---")
total_mai25 = 0
for c in CANAUX:
    v = ca25.get(c, 0)
    total_mai25 += v
    print(f"  {c:20s}: {v:>10.2f} EUR  |  {nb25.get(c,0):>3d} factures")
print(f"  {'TOTAL':20s}: {total_mai25:>10.2f} EUR")

# ────────────────────────────────────────────────────────────────
# 10. Tableau comparatif
# ────────────────────────────────────────────────────────────────
print("\n=== TABLEAU COMPARATIF ===")
print(f"{'Canal':20s} | {'Mai 2026':>12s} | {'Avr 2026':>12s} | {'D vs M-1':>10s} | {'Mai 2025':>12s} | {'D vs A-1':>10s}")
print("-" * 85)
for c in CANAUX:
    v26 = ca26.get(c, 0)
    va26 = ca_a26.get(c, 0)
    v25 = ca25.get(c, 0)
    d_m1 = f"{(v26-va26)/va26*100:+.1f}%" if va26 != 0 else "N/A"
    d_a1 = f"{(v26-v25)/v25*100:+.1f}%" if v25 != 0 else "N/A"
    print(f"{c:20s} | {v26:>12.2f} | {va26:>12.2f} | {d_m1:>10s} | {v25:>12.2f} | {d_a1:>10s}")
print("-" * 85)
v26t = total_mai26; va26t = total_avr26; v25t = total_mai25
d_m1t = f"{(v26t-va26t)/va26t*100:+.1f}%" if va26t != 0 else "N/A"
d_a1t = f"{(v26t-v25t)/v25t*100:+.1f}%" if v25t != 0 else "N/A"
print(f"{'TOTAL':20s} | {v26t:>12.2f} | {va26t:>12.2f} | {d_m1t:>10s} | {v25t:>12.2f} | {d_a1t:>10s}")

# 3 canaux
t3_26 = ca26.get('GMS',0)+ca26.get('B2B',0)+ca26.get('Horeca',0)
t3_a26 = ca_a26.get('GMS',0)+ca_a26.get('B2B',0)+ca_a26.get('Horeca',0)
t3_25 = ca25.get('GMS',0)+ca25.get('B2B',0)+ca25.get('Horeca',0)
print(f"\nPerimetre 3 canaux:")
print(f"  Mai 2026 : {t3_26:.2f}  |  Avr 2026 : {t3_a26:.2f}  |  Mai 2025 : {t3_25:.2f}")
if t3_a26 > 0: print(f"  D vs M-1 : {(t3_26-t3_a26)/t3_a26*100:+.1f}%")
if t3_25  > 0: print(f"  D vs A-1 : {(t3_26-t3_25)/t3_25*100:+.1f}%")

# Run rate journalier
jours_ouvr = 21  # mai 2026 : 31 jours - 4 weekend - 1j ferie Ascension 29/05 -> ~21 jours ouvrables
print(f"\nRun rate journalier mai 2026 ({jours_ouvr} jours ouvrables): {total_mai26/jours_ouvr:.0f} EUR/j")
