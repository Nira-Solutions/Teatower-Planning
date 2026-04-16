import xmlrpc.client, sys, re, json
from datetime import datetime, timedelta
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'
USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
print(f"Authenticated as uid={uid}")

# 1) Get ALL GMS clients (tag 27)
gms_ids = models.execute_kw(DB, uid, PWD, 'res.partner', 'search', [[
    ['category_id', 'in', [27]],
    ['is_company', '=', True],
]])
print(f"\nTotal GMS partners: {len(gms_ids)}")

fields = ['name', 'street', 'street2', 'zip', 'city', 'phone', 'comment', 'sale_warn', 'sale_warn_msg']
partners = models.execute_kw(DB, uid, PWD, 'res.partner', 'read', [gms_ids], {'fields': fields})

EXCLUDE_NAMES = ['Delhaize Le Lion', 'Carrefour Belgium']
active_partners = []
arret_partners = []
for p in partners:
    if p['name'] in EXCLUDE_NAMES:
        continue
    if p.get('sale_warn') == 'block' or (p.get('comment') and '[ARRET' in str(p['comment'])):
        arret_partners.append(p)
        continue
    active_partners.append(p)

print(f"Active GMS (excl Arret + centraux): {len(active_partners)}")
print(f"Arret: {len(arret_partners)}")

# 2) Get confirmed sale orders for active partners
active_ids = [p['id'] for p in active_partners]

orders = models.execute_kw(DB, uid, PWD, 'sale.order', 'search_read', [[
    ['partner_id', 'in', active_ids],
    ['state', 'in', ['sale', 'done']],
]], {'fields': ['partner_id', 'name', 'date_order', 'amount_total', 'state'], 'order': 'date_order desc'})
print(f"Total confirmed orders: {len(orders)}")

# 3) Get recent pickings (done in last 21 days)
cutoff = (datetime(2026, 4, 15) - timedelta(days=21)).strftime('%Y-%m-%d')
pickings = models.execute_kw(DB, uid, PWD, 'stock.picking', 'search_read', [[
    ['partner_id', 'in', active_ids],
    ['state', '=', 'done'],
    ['date_done', '>=', cutoff],
    ['picking_type_id.code', '=', 'outgoing'],
]], {'fields': ['partner_id', 'name', 'date_done', 'origin'], 'order': 'date_done desc'})
print(f"Recent done pickings (last 21d): {len(pickings)}")

# 4) Build scoring per partner
partner_orders = defaultdict(list)
for o in orders:
    pid = o['partner_id'][0]
    partner_orders[pid].append(o)

today = datetime(2026, 4, 15)

results = []
for p in active_partners:
    pid = p['id']
    ords = partner_orders.get(pid, [])

    total_ca = sum(o['amount_total'] for o in ords)
    n_orders = len(ords)
    ca_per_order = total_ca / n_orders if n_orders else 0

    if ords:
        dates = sorted([datetime.strptime(o['date_order'][:10], '%Y-%m-%d') for o in ords])
        days_since_last = (today - dates[-1]).days
        if len(dates) > 1:
            intervals = [(dates[i+1]-dates[i]).days for i in range(len(dates)-1)]
            order_freq = sum(intervals) / len(intervals)
        else:
            order_freq = 999
    else:
        days_since_last = 999
        order_freq = 999

    if ca_per_order >= 500 and total_ca >= 4000:
        tier = 'A'
        max_days = 20
    elif ca_per_order >= 300 and total_ca >= 2000:
        tier = 'B'
        max_days = 35
    elif n_orders > 0 and days_since_last <= 180:
        tier = 'C'
        max_days = 50
    else:
        tier = 'D'
        max_days = 999

    overdue = days_since_last > max_days

    zip_code = p.get('zip', '') or ''
    zone = 'UNKNOWN'
    if zip_code.startswith('5'):
        zone = 'NAMUR'
    elif zip_code.startswith('4'):
        zone = 'LIEGE'
    elif zip_code.startswith('6'):
        zone = 'LUXEMBOURG_HAINAUT'
    elif zip_code.startswith('7'):
        zone = 'HAINAUT'
    elif len(zip_code) >= 4:
        zn = int(zip_code[:4]) if zip_code[:4].isdigit() else 0
        if 1300 <= zn <= 1999:
            zone = 'BW'
        elif 1000 <= zn <= 1299:
            zone = 'BRUXELLES'

    results.append({
        'id': pid,
        'name': p['name'],
        'street': p.get('street', ''),
        'zip': zip_code,
        'city': p.get('city', ''),
        'phone': p.get('phone', ''),
        'comment': (p.get('comment') or '')[:500],
        'zone': zone,
        'tier': tier,
        'max_days': max_days,
        'total_ca': round(total_ca, 2),
        'n_orders': n_orders,
        'ca_per_order': round(ca_per_order, 2),
        'days_since_last': days_since_last,
        'order_freq': round(order_freq, 1),
        'overdue': overdue,
        'last_order': ords[0]['name'] if ords else None,
        'last_order_date': ords[0]['date_order'][:10] if ords else None,
        'last_order_amount': ords[0]['amount_total'] if ords else None,
    })

results.sort(key=lambda r: (r['zone'], r['tier'], -r['days_since_last']))

partner_pickings = defaultdict(list)
for pk in pickings:
    pid = pk['partner_id'][0]
    partner_pickings[pid].append(pk)

# Print ALL active clients grouped by zone
for zone in ['HAINAUT', 'NAMUR', 'LIEGE', 'LUXEMBOURG_HAINAUT', 'BW', 'BRUXELLES', 'UNKNOWN']:
    zone_clients = [r for r in results if r['zone'] == zone]
    if not zone_clients:
        continue
    print(f"\n{'='*80}")
    print(f"ZONE: {zone} ({len(zone_clients)} clients)")
    print(f"{'='*80}")
    for r in zone_clients:
        flag = " ** OVERDUE **" if r['overdue'] else ""
        recent_pick = partner_pickings.get(r['id'], [])
        pick_info = ""
        if recent_pick:
            pick_info = f" | PICK: {recent_pick[0]['name']} ({recent_pick[0]['date_done'][:10]})"
        print(f"  [{r['tier']}] {r['name']} (ID:{r['id']}) | {r['street']}, {r['zip']} {r['city']} | tel:{r['phone']}")
        print(f"      CA:{r['total_ca']}E | CA/cmd:{r['ca_per_order']}E | {r['n_orders']}cmd | last:{r['last_order']} ({r['last_order_date']}) {r['last_order_amount']}E | {r['days_since_last']}j/{r['max_days']}j{flag}{pick_info}")
        if r['comment']:
            clean = re.sub(r'<[^>]+>', ' ', r['comment']).strip()[:200]
            if clean:
                print(f"      NOTE: {clean}")

# IDs already planned this week
ALREADY_PLANNED_IDS = [
    9046, 2812, 3297, 2821, 2958, 2909, 3210, 115879,
    2905, 7692, 2773, 7678, 8558, 2979, 2811
]

# Also need to find IDs for Spar Namur, Delhaize Gosselies, Proxy Couronne, Torrefactory
spar_ids = models.execute_kw(DB, uid, PWD, 'res.partner', 'search', [[
    ['name', 'ilike', 'NDB Diffusion'],
    ['is_company', '=', True],
]])
print(f"\nNDB Diffusion (Spar Namur): {spar_ids}")
ALREADY_PLANNED_IDS.extend(spar_ids)

print(f"\n{'='*80}")
print(f"CANDIDATES FOR ADDITIONAL VISITS (not already planned, tier A/B/C)")
print(f"{'='*80}")

for zone in ['HAINAUT', 'NAMUR', 'LIEGE', 'LUXEMBOURG_HAINAUT']:
    zone_clients = [r for r in results if r['zone'] == zone and r['id'] not in ALREADY_PLANNED_IDS and r['tier'] in ['A','B','C']]
    if not zone_clients:
        continue
    print(f"\n--- {zone} ---")
    for r in zone_clients:
        flag = " ** OVERDUE **" if r['overdue'] else ""
        recent_pick = partner_pickings.get(r['id'], [])
        pick_info = ""
        if recent_pick:
            pick_info = f" | PICK: {recent_pick[0]['name']} ({recent_pick[0]['date_done'][:10]})"
        print(f"  [{r['tier']}] {r['name']} (ID:{r['id']}) | {r['street']}, {r['zip']} {r['city']} | {r['days_since_last']}j/{r['max_days']}j{flag}{pick_info}")
        if r['comment']:
            clean = re.sub(r'<[^>]+>', ' ', r['comment']).strip()[:150]
            if clean:
                print(f"      NOTE: {clean}")

# 5) Get existing calendar events for week 20-24 april
events = models.execute_kw(DB, uid, PWD, 'calendar.event', 'search_read', [[
    ['start', '>=', '2026-04-19 22:00:00'],
    ['start', '<', '2026-04-25 00:00:00'],
]], {'fields': ['name', 'start', 'stop', 'partner_ids', 'user_id', 'location', 'id'], 'order': 'start'})
print(f"\n{'='*80}")
print(f"EXISTING CALENDAR EVENTS week 20-24 April: {len(events)}")
print(f"{'='*80}")
for ev in events:
    print(f"  #{ev['id']} | {ev['start']} - {ev['stop']} | user:{ev['user_id']} | {ev['name']}")

# Save results for later use
with open('planning/_scan_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("\nResults saved to planning/_scan_results.json")
