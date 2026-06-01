import xmlrpc.client

URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model,method,args,kw=None): return m.execute_kw(DB,uid,PWD,model,method,args,kw or {})

print(f"Connected as uid={uid}")

# 1. Sales teams
teams = call('crm.team', 'search_read', [[]], {'fields': ['id','name'], 'limit': 50})
print("\n=== SALES TEAMS ===")
for t in teams: print(t)

# 2. POS configs
pos_configs = call('pos.config', 'search_read', [[]], {'fields': ['id','name'], 'limit': 20})
print("\n=== POS CONFIGS ===")
for p in pos_configs: print(p)

# 3. Sources (utm.source) pour identifier Shopify sur sale.order
try:
    sources = call('utm.source', 'search_read', [[]], {'fields': ['id','name'], 'limit': 50})
    print("\n=== UTM SOURCES ===")
    for s in sources: print(s)
except Exception as e:
    print(f"utm.source error: {e}")

# 4. Sample sale.order fields available (check source_id, team_id)
sample_so = call('sale.order', 'search_read',
    [[ ['date_order','>=','2025-10-15'], ['date_order','<=','2025-12-31'], ['state','in',['sale','done']] ]],
    {'fields': ['id','name','amount_total','team_id','source_id','state','date_order'], 'limit': 5})
print("\n=== SAMPLE SALE.ORDERS (ref period) ===")
for s in sample_so: print(s)
