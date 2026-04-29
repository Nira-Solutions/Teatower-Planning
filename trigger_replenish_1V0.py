"""
Trigger replenish sur les OP TT/Stock des produits 1V0 pour verifier
que les MO se generent maintenant que la route Manufacture est en place.
"""
import xmlrpc.client, json
from datetime import datetime, timedelta

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PW = "Teatower123"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PW, {})
m = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)
def call(model, method, args=None, kwargs=None):
    return m.execute_kw(DB, uid, PW, model, method, args or [], kwargs or {})

print(f"UID = {uid}")

# 1) Tous les OP des produits 1V0 sur TT/Stock avec qty_to_order > 0
v_ids = call('product.product', 'search', [[('default_code', '=ilike', '1V0%')]])
loc_tt = call('stock.location', 'search', [[('complete_name', '=', 'TT/Stock')]])[0]

ops = call('stock.warehouse.orderpoint', 'search_read',
           [[('product_id', 'in', v_ids), ('location_id', '=', loc_tt)]],
           {'fields': ['id', 'product_id', 'route_id', 'qty_to_order', 'qty_forecast',
                       'product_min_qty', 'product_max_qty']})

print(f"OP trouvés : {len(ops)}")
to_replenish = [op for op in ops if (op.get('qty_to_order') or 0) > 0]
print(f"OP avec qty_to_order > 0 : {len(to_replenish)}")
for op in to_replenish:
    print(f"  OP/{op['id']} {op['product_id'][1][:35]:35s} qty_to_order={op['qty_to_order']} forecast={op['qty_forecast']}")

if not to_replenish:
    print("Rien à réapprovisionner — soit le forecast est OK, soit le scheduler n'a pas encore tourné.")
    # Forcer le scheduler
    print("\nDéclenchement du scheduler global...")
    try:
        call('procurement.group', 'run_scheduler')
        print("Scheduler lancé.")
    except Exception as e:
        print(f"Erreur scheduler : {e}")
else:
    op_ids = [op['id'] for op in to_replenish]
    print(f"\nLancement action_replenish sur {len(op_ids)} OP...")
    try:
        result = call('stock.warehouse.orderpoint', 'action_replenish', [op_ids])
        print(f"Résultat : {result}")
    except Exception as e:
        print(f"Erreur action_replenish : {e}")

# Verifier les MO créés depuis quelques minutes
print("\n--- Vérification MO créés récemment ---")
since = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
recent_mo = call('mrp.production', 'search_read',
                 [[('product_id', 'in', v_ids), ('create_date', '>=', since)]],
                 {'fields': ['id', 'name', 'product_id', 'product_qty', 'state', 'create_date'],
                  'order': 'create_date desc'})
print(f"MO créés depuis {since} sur produits 1V0 : {len(recent_mo)}")
for mo in recent_mo[:20]:
    print(f"  {mo['name']} | {mo['product_id'][1][:35]:35s} | qty={mo['product_qty']} | state={mo['state']} | {mo['create_date']}")

# Sauvegarde
with open('odoo/_replenish_1V0_2026-04-29.json', 'w', encoding='utf-8') as f:
    json.dump({
        'op_total': len(ops),
        'op_to_replenish': len(to_replenish),
        'mo_created_since': since,
        'mo_created_count': len(recent_mo),
        'mo_sample': recent_mo[:30],
    }, f, ensure_ascii=False, indent=2, default=str)
print("[ecrit] odoo/_replenish_1V0_2026-04-29.json")
