"""
Script Data-BI : CA mai 2026 par canal — version corrigee avec parents + overrides
"""
import xmlrpc.client
from collections import defaultdict

URL = 'https://tea-tree.odoo.com'; DB = 'tsc-be-tea-tree-main-18515272'
USER = 'nicolas.raes@teatower.com'; PWD = 'Teatower123'
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m, meth, args, kw=None): return models.execute_kw(DB, uid, PWD, m, meth, args, kw or {})

GMS_TAGS    = {88, 27}
HORECA_TAGS = {84, 26}
B2B_TAGS    = {85}
SHOPIFY_TAGS = {86}
MAG_JOURNALS = {22, 24, 25, 37, 30}

def load_invoices(date_from, date_to, label=""):
    inv = call('account.move', 'search_read',
        [[('move_type','in',['out_invoice','out_refund']),
          ('state','=','posted'),
          ('invoice_date','>=',date_from),
          ('invoice_date','<=',date_to)]],
        {'fields':['name','invoice_date','amount_untaxed','move_type',
                   'partner_id','journal_id','invoice_origin'], 'limit': 3000})
    print(f"[{label}] {len(inv)} factures/avoirs")
    return inv

def load_partner_info(invoices):
    pids = list(set(i['partner_id'][0] for i in invoices if i['partner_id']))
    ptags = {}
    for i in range(0, len(pids), 100):
        chunk = pids[i:i+100]
        ps = call('res.partner','read',[chunk],{'fields':['id','name','category_id','parent_id']})
        for p in ps:
            raw = p['category_id']
            cats = [c[0] if isinstance(c,(list,tuple)) else c for c in raw] if raw else []
            ptags[p['id']] = {'name': p['name'], 'cats': cats, 'parent': p['parent_id']}
    # Charger les parents
    parent_pids = list(set(v['parent'][0] for v in ptags.values() if v['parent']))
    pparent = {}
    for i in range(0, len(parent_pids), 100):
        chunk = parent_pids[i:i+100]
        ps = call('res.partner','read',[chunk],{'fields':['id','name','category_id']})
        for p in ps:
            raw = p['category_id']
            cats = [c[0] if isinstance(c,(list,tuple)) else c for c in raw] if raw else []
            pparent[p['id']] = {'name': p['name'], 'cats': cats}
    return ptags, pparent

def get_partner_name(pid, ptags, pparent):
    pinfo = ptags.get(pid, {})
    pname = pinfo.get('name')
    if not isinstance(pname, str) or not pname:
        parent = pinfo.get('parent')
        if parent:
            pname = pparent.get(parent[0], {}).get('name', f'Partner#{pid}')
        else:
            pname = f'Partner#{pid}'
    return pname

def classify(inv, ptags, pparent):
    if not inv['partner_id']:
        return 'Autres'
    pid = inv['partner_id'][0]
    pinfo = ptags.get(pid, {})
    cats = set(pinfo.get('cats', []))
    raw_name = pinfo.get('name')
    pname = raw_name.lower() if isinstance(raw_name, str) else ''
    jid = inv['journal_id'][0] if inv['journal_id'] else 0

    # Journaux magasins -> POS
    if jid in MAG_JOURNALS:
        return 'POS'

    # Shopify/Amazon par origin
    origin = (inv.get('invoice_origin') or '').lower()
    if 'shopify' in origin:
        return 'Shopify'
    if 'amazon' in origin or 'fba' in origin:
        return 'Amazon'

    # Heriter les tags du parent (adresses de facturation)
    parent_info = pinfo.get('parent')
    if parent_info:
        parent_id = parent_info[0]
        pcats = set(pparent.get(parent_id, {}).get('cats', []))
        cats = cats | pcats
        # Nom du parent pour override
        parent_name = (pparent.get(parent_id, {}).get('name') or '').lower()
    else:
        parent_name = ''

    # Override nom GMS (KAIO tagué Shopify mais c'est un Delhaize)
    name_check = pname or parent_name
    if any(x in name_check for x in ['delhaize','carrefour','intermarche','spar match']):
        return 'GMS'

    # Tags canal
    if cats & GMS_TAGS:
        return 'GMS'
    if cats & HORECA_TAGS:
        return 'Horeca'
    if cats & B2B_TAGS:
        return 'B2B'
    if cats & SHOPIFY_TAGS:
        return 'Shopify'

    # Override nom pour non-tagges connus
    if any(x in name_check for x in ['mix f&b','brasserie','cafe','torrefactory','catering','leisure','hotel']):
        return 'Horeca'
    if any(x in name_check for x in ['hello bio','silversquare','d ici','cocoricoop','epicerie','bio sprl']):
        return 'B2B'

    return 'Autres'

def ventiler(invoices, ptags, pparent):
    ca = defaultdict(float)
    nb_inv = defaultdict(int)
    clients = defaultdict(set)
    avoirs = defaultdict(float)
    top_clients = defaultdict(lambda: defaultdict(float))

    for inv in invoices:
        canal = classify(inv, ptags, pparent)
        sign = -1 if inv['move_type'] == 'out_refund' else 1
        amt = inv['amount_untaxed'] * sign
        ca[canal] += amt
        nb_inv[canal] += 1
        if inv['partner_id']:
            pid = inv['partner_id'][0]
            clients[canal].add(pid)
            top_clients[canal][pid] += amt
        if inv['move_type'] == 'out_refund':
            avoirs[canal] += inv['amount_untaxed']

    return ca, nb_inv, clients, avoirs, top_clients

CANAUX = ['GMS','B2B','Horeca','POS','Shopify','Amazon','Autres']

# ── MAI 2026 ──────────────────────────────────────────────────────
print("\n=== MAI 2026 ===")
inv26 = load_invoices('2026-05-01','2026-05-31','MAI 2026')
ptags26, pparent26 = load_partner_info(inv26)
ca26, nb26, cli26, av26, top26 = ventiler(inv26, ptags26, pparent26)

print("\n--- CA MAI 2026 ---")
total26 = 0
for c in CANAUX:
    v = ca26.get(c,0); total26 += v
    print(f"  {c:20s}: {v:>10.2f} EUR  | {nb26.get(c,0):>4d} fac  | {len(cli26.get(c,set())):>3d} cli")
print(f"  {'TOTAL':20s}: {total26:>10.2f} EUR")
t3_26 = ca26.get('GMS',0)+ca26.get('B2B',0)+ca26.get('Horeca',0)
print(f"  3 canaux: {t3_26:.2f}")
print(f"  Avoirs: GMS={av26.get('GMS',0):.2f}  B2B={av26.get('B2B',0):.2f}  Horeca={av26.get('Horeca',0):.2f}  POS={av26.get('POS',0):.2f}  Autres={av26.get('Autres',0):.2f}")

print("\n--- TOP 5 CLIENTS MAI 2026 ---")
for canal in ['GMS','Horeca','B2B']:
    tc = top26.get(canal,{})
    sorted_c = sorted(tc.items(), key=lambda x: -x[1])[:5]
    print(f"\n{canal} ({ca26.get(canal,0):.2f} EUR):")
    for pid, amt in sorted_c:
        pname = get_partner_name(pid, ptags26, pparent26)
        print(f"    {str(pname):50s}  {amt:>10.2f}")

print("\n--- Autres residuels ---")
top_autres = sorted(top26.get('Autres',{}).items(), key=lambda x:-x[1])[:15]
for pid, amt in top_autres:
    pname = get_partner_name(pid, ptags26, pparent26)
    cats = ptags26.get(pid,{}).get('cats',[])
    print(f"  pid={pid}  {str(pname):50s}  cats={cats}  amt={amt:.2f}")

# ── AVRIL 2026 ────────────────────────────────────────────────────
print("\n=== AVRIL 2026 (reel clos) ===")
inv_a26 = load_invoices('2026-04-01','2026-04-30','AVRIL 2026')
ptags_a26, pparent_a26 = load_partner_info(inv_a26)
ca_a26, nb_a26, cli_a26, av_a26, top_a26 = ventiler(inv_a26, ptags_a26, pparent_a26)

total_a26 = 0
for c in CANAUX:
    v = ca_a26.get(c,0); total_a26 += v
print(f"  TOTAL avril 2026: {total_a26:.2f}")
for c in CANAUX:
    print(f"  {c:20s}: {ca_a26.get(c,0):>10.2f}")
t3_a26 = ca_a26.get('GMS',0)+ca_a26.get('B2B',0)+ca_a26.get('Horeca',0)
print(f"  3 canaux: {t3_a26:.2f}")

# ── MAI 2025 ─────────────────────────────────────────────────────
print("\n=== MAI 2025 (reel clos) ===")
inv25 = load_invoices('2025-05-01','2025-05-31','MAI 2025')
ptags25, pparent25 = load_partner_info(inv25)
ca25, nb25, cli25, av25, top25 = ventiler(inv25, ptags25, pparent25)

total25 = 0
for c in CANAUX:
    v = ca25.get(c,0); total25 += v
print(f"  TOTAL mai 2025: {total25:.2f}")
for c in CANAUX:
    print(f"  {c:20s}: {ca25.get(c,0):>10.2f}")
t3_25 = ca25.get('GMS',0)+ca25.get('B2B',0)+ca25.get('Horeca',0)
print(f"  3 canaux: {t3_25:.2f}")

# Identifier les gros comptes B2B 2025 (Va.S.Co ?)
print("\n  Top B2B 2025:")
top_b2b25 = sorted(top25.get('B2B',{}).items(), key=lambda x:-x[1])[:5]
for pid, amt in top_b2b25:
    pname = get_partner_name(pid, ptags25, pparent25)
    print(f"    {str(pname):50s}  {amt:>10.2f}")

print("\n  Top Autres 2025:")
top_oth25 = sorted(top25.get('Autres',{}).items(), key=lambda x:-x[1])[:10]
for pid, amt in top_oth25:
    pname = get_partner_name(pid, ptags25, pparent25)
    cats = ptags25.get(pid,{}).get('cats',[])
    print(f"    {str(pname):50s}  cats={cats}  amt={amt:.2f}")

# ── TABLEAU COMPARATIF ────────────────────────────────────────────
print("\n=== TABLEAU COMPARATIF ===")
print(f"{'Canal':20s} | {'Mai 2026':>12s} | {'Avr 2026':>12s} | {'D vs M-1':>10s} | {'Mai 2025':>12s} | {'D vs A-1':>10s}")
print("-" * 90)
for c in CANAUX:
    v26 = ca26.get(c,0); va26 = ca_a26.get(c,0); v25 = ca25.get(c,0)
    d_m1 = f"{(v26-va26)/va26*100:+.1f}%" if va26 != 0 else "N/A"
    d_a1 = f"{(v26-v25)/v25*100:+.1f}%" if v25 != 0 else "N/A"
    print(f"  {c:18s} | {v26:>12.2f} | {va26:>12.2f} | {d_m1:>10s} | {v25:>12.2f} | {d_a1:>10s}")
print("-" * 90)
d_m1t = f"{(total26-total_a26)/total_a26*100:+.1f}%" if total_a26 != 0 else "N/A"
d_a1t = f"{(total26-total25)/total25*100:+.1f}%" if total25 != 0 else "N/A"
print(f"  {'TOTAL':18s} | {total26:>12.2f} | {total_a26:>12.2f} | {d_m1t:>10s} | {total25:>12.2f} | {d_a1t:>10s}")
print()
d3_m1 = f"{(t3_26-t3_a26)/t3_a26*100:+.1f}%" if t3_a26 != 0 else "N/A"
d3_a1 = f"{(t3_26-t3_25)/t3_25*100:+.1f}%" if t3_25 != 0 else "N/A"
print(f"  3 canaux: mai26={t3_26:.2f}  avr26={t3_a26:.2f}  {d3_m1}  mai25={t3_25:.2f}  {d3_a1}")

jours_ouvr = 20  # mai 2026: 21 calendrier - 1 Ascension 29/05 = 20 jours ouvrables nets
print(f"\nRun rate journalier ({jours_ouvr}j ouvrables): {total26/jours_ouvr:.0f} EUR/j")
