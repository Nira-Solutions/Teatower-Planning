"""
Diagnostic urgence 2026-04-29 : MO ne se generent plus pour 1V0 (vrac intermediaire) sur TT/Stock.
"""
import xmlrpc.client, json, os
from collections import Counter

URL = "https://tea-tree.odoo.com"
DB  = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PW  = "Teatower123"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PW, {})
print(f"UID = {uid}")
m = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def call(model, method, args=None, kwargs=None):
    return m.execute_kw(DB, uid, PW, model, method, args or [], kwargs or {})

os.makedirs('odoo', exist_ok=True)

# ============================================================================
# 1) Identifier ce que recouvre "1V0"
# ============================================================================
print("\n=== 1) Produits dont default_code commence par '1V0' ===")
domain_1V0 = [('default_code', '=ilike', '1V0%')]
v_ids = call('product.product', 'search', [domain_1V0])
print(f"product.product '1V0%' : {len(v_ids)} variantes")

if v_ids:
    sample = call('product.product', 'read', [v_ids[:30]], {
        'fields': ['id', 'default_code', 'name', 'active', 'product_tmpl_id', 'route_ids']
    })
    for v in sample[:15]:
        rids = v.get('route_ids') or []
        print(f"  {v['id']:6d} {v['default_code']:10s} active={v['active']} routes={rids} {v['name'][:50]}")

# Distribution par prefixe
print("\n=== 2) Distribution prefixes 'V0' sur templates ===")
all_v_ids = call('product.template', 'search', [[('default_code', 'ilike', 'V0')]])
print(f"templates contenant 'V0' : {len(all_v_ids)}")
if all_v_ids:
    rows = call('product.template', 'read', [all_v_ids], {'fields': ['default_code']})
    prefixes = Counter()
    for t in rows:
        code = (t.get('default_code') or '')
        idx = code.find('V0')
        if idx >= 0:
            prefixes[code[:idx]] += 1
    for p, c in prefixes.most_common(15):
        print(f"  '{p}' : {c}")

# ============================================================================
# 3) Routes sur les templates 1V0
# ============================================================================
print("\n=== 3) Routes des templates 1V0 ===")
tmpl_1V0_ids = call('product.template', 'search', [[('default_code', '=ilike', '1V0%')]])
print(f"templates 1V0 : {len(tmpl_1V0_ids)}")

# Map des routes
route_map = {r['id']: r['name'] for r in
             call('stock.route', 'search_read', [[]], {'fields': ['id', 'name']})}
print(f"Routes connues : {route_map}")

if tmpl_1V0_ids:
    tmpls = call('product.template', 'read', [tmpl_1V0_ids], {
        'fields': ['id', 'default_code', 'name', 'route_ids', 'active']
    })
    counter_routes = Counter()
    no_route = []
    for t in tmpls:
        rs = tuple(sorted(t.get('route_ids') or []))
        counter_routes[rs] += 1
        if not rs:
            no_route.append(t)
    print(f"\nDistribution route_ids sur templates 1V0 :")
    for rs, c in counter_routes.most_common():
        names = [route_map.get(r, f"?{r}") for r in rs]
        print(f"  {rs} ({names}) : {c}")
    print(f"\nTemplates 1V0 sans route : {len(no_route)}")
    for t in no_route[:10]:
        print(f"  tmpl {t['id']} {t['default_code']:10s} {t['name'][:50]}")

# ============================================================================
# 4) BoM sur les 1V0
# ============================================================================
print("\n=== 4) BoM sur templates 1V0 ===")
if tmpl_1V0_ids:
    boms = call('mrp.bom', 'search_read',
                [[('product_tmpl_id', 'in', tmpl_1V0_ids), ('active', '=', True)]],
                {'fields': ['id', 'product_tmpl_id', 'product_qty', 'type', 'code', 'active']})
    print(f"BoM actives : {len(boms)} (sur {len(tmpl_1V0_ids)} templates)")
    types = Counter(b['type'] for b in boms)
    print(f"Types BoM : {dict(types)}")
    tmpl_with_bom = {b['product_tmpl_id'][0] for b in boms}
    tmpl_without_bom = [tid for tid in tmpl_1V0_ids if tid not in tmpl_with_bom]
    print(f"Templates 1V0 SANS BoM active : {len(tmpl_without_bom)}")
    if tmpl_without_bom:
        rows = call('product.template', 'read', [tmpl_without_bom[:10]], {'fields': ['id', 'default_code', 'name']})
        for t in rows:
            print(f"  tmpl {t['id']} {t['default_code']:10s} {t['name'][:50]}")

# ============================================================================
# 5) Orderpoints TT/Stock sur les 1V0
# ============================================================================
print("\n=== 5) Orderpoints TT/Stock pour 1V0 ===")
loc_tt = call('stock.location', 'search_read',
              [[('complete_name', '=', 'TT/Stock')]], {'fields': ['id', 'name', 'complete_name']})
print(f"Location TT/Stock : {loc_tt}")
if loc_tt and v_ids:
    loc_id = loc_tt[0]['id']
    ops = call('stock.warehouse.orderpoint', 'search_read',
               [[('product_id', 'in', v_ids), ('location_id', '=', loc_id)]],
               {'fields': ['id', 'product_id', 'route_id', 'product_min_qty',
                           'product_max_qty', 'qty_to_order', 'qty_forecast', 'active', 'trigger']})
    print(f"OP TT/Stock sur produits 1V0 : {len(ops)}")
    no_route_ops = [op for op in ops if not op.get('route_id')]
    print(f"  -> sans route_id : {len(no_route_ops)}")
    print(f"  -> avec qty_to_order > 0 : {sum(1 for op in ops if (op.get('qty_to_order') or 0) > 0)}")
    for op in ops[:8]:
        rid = op.get('route_id')
        rname = (rid[1] if isinstance(rid, list) else None)
        print(f"  OP/{op['id']} {op['product_id'][1][:25]:25s} "
              f"route={rname} min={op['product_min_qty']} max={op['product_max_qty']} "
              f"to_order={op.get('qty_to_order')} forecast={op.get('qty_forecast')} active={op['active']}")

# ============================================================================
# 6) Routes attachees au WH TT
# ============================================================================
print("\n=== 6) Routes du Warehouse TT ===")
whs = call('stock.warehouse', 'search_read', [[]], {'fields': ['id', 'name', 'code', 'route_ids']})
for wh in whs:
    rnames = [route_map.get(r, f"?{r}") for r in (wh.get('route_ids') or [])]
    print(f"  WH {wh['id']} {wh['code']} ({wh['name']}) routes={rnames}")

# ============================================================================
# 7) MO recents sur les 1V0
# ============================================================================
print("\n=== 7) MO sur les 1V0 (30 derniers jours) ===")
from datetime import datetime, timedelta
since = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
if v_ids:
    mo_count = call('mrp.production', 'search_count',
                    [[('product_id', 'in', v_ids), ('create_date', '>=', since)]])
    print(f"MO crees depuis {since} sur 1V0 : {mo_count}")
    mo_states = call('mrp.production', 'read_group',
                     [[('product_id', 'in', v_ids), ('create_date', '>=', since)],
                      ['state'], ['state']])
    for g in mo_states:
        print(f"  {g['state']}: {g['state_count']}")

# ============================================================================
# Sauvegarde
# ============================================================================
print("\n=== Diagnostic OK — sauvegarde JSON ===")
out = {
    'variants_1V0_count': len(v_ids),
    'templates_1V0_count': len(tmpl_1V0_ids),
    'route_map': route_map,
    'route_distribution_on_tmpl': {str(k): v for k, v in counter_routes.most_common()} if tmpl_1V0_ids else {},
    'tmpl_without_bom_count': len(tmpl_without_bom) if tmpl_1V0_ids else 0,
    'op_tt_count': len(ops) if (loc_tt and v_ids) else 0,
    'op_tt_without_route_count': len(no_route_ops) if (loc_tt and v_ids) else 0,
    'wh_routes': {wh['code']: [route_map.get(r, f"?{r}") for r in (wh.get('route_ids') or [])] for wh in whs},
}
with open('odoo/_diag_1V0_2026-04-29.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
print("[ecrit] odoo/_diag_1V0_2026-04-29.json")
print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
