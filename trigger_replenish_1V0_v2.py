"""
Replenish v2 : retry, range elargi, et check des MO.
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

# 1) Tous OP 1V0 sur TT/Stock avec qty_to_order > 0
v_ids = call('product.product', 'search', [[('default_code', '=ilike', '1V0%')]])
loc_tt = call('stock.location', 'search', [[('complete_name', '=', 'TT/Stock')]])[0]
ops = call('stock.warehouse.orderpoint', 'search_read',
           [[('product_id', 'in', v_ids), ('location_id', '=', loc_tt)]],
           {'fields': ['id', 'product_id', 'qty_to_order', 'qty_forecast']})
to_replenish = [op for op in ops if (op.get('qty_to_order') or 0) > 0]
op_ids = [op['id'] for op in to_replenish]
print(f"OP a replenish : {len(op_ids)} | ids: {op_ids}")

# 2) Lancer action_replenish (peut retourner False si pas d'action wizard a afficher,
# c'est normal — le travail est fait en side-effect)
print("\n>>> action_replenish")
res = call('stock.warehouse.orderpoint', 'action_replenish', [op_ids])
print(f"   result: {res}")

# 3) Verifier MO crees aujourd'hui (range elargi pour timezone)
print("\n--- MO sur 1V0 aujourd'hui ---")
today = (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')
mos = call('mrp.production', 'search_read',
           [[('product_id', 'in', v_ids), ('create_date', '>=', today)]],
           {'fields': ['id', 'name', 'product_id', 'product_qty', 'state', 'create_date',
                       'origin', 'orderpoint_id'],
            'order': 'create_date desc'})
print(f"MO recents : {len(mos)}")
for mo in mos[:30]:
    print(f"  {mo['name']:14s} | {mo['product_id'][1][:35]:35s} | qty={mo['product_qty']:>5} | "
          f"state={mo['state']:<10s} | OP={mo.get('orderpoint_id')} | {mo['create_date']}")

# 4) Verifier qty_to_order apres
print("\n--- qty_to_order apres ---")
ops_after = call('stock.warehouse.orderpoint', 'read', [op_ids],
                 {'fields': ['id', 'product_id', 'qty_to_order', 'qty_forecast']})
for op in ops_after:
    print(f"  OP/{op['id']} {op['product_id'][1][:30]:30s} qty_to_order={op['qty_to_order']} forecast={op['qty_forecast']}")

# 5) Si rien ne se passe, essayer le run_scheduler global
if len(mos) == 0:
    print("\n>>> Aucun MO. Lancement scheduler global...")
    try:
        call('procurement.group', 'run_scheduler')
        print("   scheduler OK")
    except Exception as e:
        print(f"   scheduler erreur: {e}")

    # Re-check
    today2 = (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')
    mos2 = call('mrp.production', 'search_read',
                [[('product_id', 'in', v_ids), ('create_date', '>=', today2)]],
                {'fields': ['id', 'name', 'product_id', 'product_qty', 'state']})
    print(f"   MO apres scheduler : {len(mos2)}")
    for mo in mos2[:20]:
        print(f"     {mo['name']} {mo['product_id'][1][:35]} qty={mo['product_qty']} state={mo['state']}")
