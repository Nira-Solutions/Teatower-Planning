"""Fetch Odoo data for Teatower Cockpit.
Produit cockpit_data.json consommé par teatower_cockpit.html.
Read-only. Lance manuellement ou via cron (toutes les 15 min par ex).
"""
import xmlrpc.client, json, datetime, sys, traceback

URL  = "https://tea-tree.odoo.com"
DB   = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD  = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, USER, PWD, {})
if not uid:
    sys.exit("AUTH KO")
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
def rpc(m,fn,a,k=None): return models.execute_kw(DB,uid,PWD,m,fn,a,k or {})

today = datetime.date.today()
start30 = (today - datetime.timedelta(days=30)).isoformat()

data = {"generated_at": datetime.datetime.now().isoformat(), "source": "odoo-live"}

# === ORDERS (devis à valider < 24h) ===
try:
    quotes = rpc('sale.order','search_read',
        [[['state','in',['draft','sent']]]],
        {'fields':['name','partner_id','amount_total','date_order','validity_date'],
         'limit':20,'order':'date_order desc'})
    orders = []
    for q in quotes:
        d = q.get('validity_date') or q.get('date_order') or ''
        try:
            due = datetime.date.fromisoformat(d[:10])
            due_h = max(0, int((due - today).total_seconds()/3600) + 24)
        except Exception:
            due_h = 48
        orders.append({
            'id': q['name'],
            'client': (q['partner_id'] or ['',''])[1] if q.get('partner_id') else '—',
            'amount': round(q['amount_total'] or 0),
            'dueH': due_h,
            'status': 'pending',
        })
    data['orders'] = [o for o in orders if o['dueH'] < 72][:8]
except Exception as e:
    data['orders_error'] = str(e)

# === STORES (clients GMS actifs — CA 30j) ===
try:
    # On cherche les partenaires qui ont une commande facturée sur 30j
    invoices = rpc('account.move','search_read',
        [[['move_type','=','out_invoice'],['state','=','posted'],['invoice_date','>=',start30]]],
        {'fields':['partner_id','amount_untaxed'],'limit':2000})
    by_p = {}
    for inv in invoices:
        p = inv.get('partner_id')
        if not p: continue
        pid = p[0]; pname = p[1]
        by_p.setdefault(pid, {'name':pname,'ca':0})
        by_p[pid]['ca'] += inv.get('amount_untaxed') or 0
    top = sorted(by_p.items(), key=lambda x:-x[1]['ca'])[:10]
    stores = []
    for i,(pid,info) in enumerate(top):
        ca = round(info['ca'])
        # delta & stockout : approximation par absence de données récentes
        stores.append({
            'id': f'P{pid}',
            'name': info['name'][:40],
            'ca30': ca,
            'delta': 0.0,
            'stockout': 0.0,
            'score': 70,
            'risk': 'green',
            'visits': 0,
        })
    data['stores'] = stores
except Exception as e:
    data['stores_error'] = str(e)
    data['stores'] = []

# === PRODUCTS TOP/FLOP (lignes facturées 30j) ===
try:
    lines = rpc('account.move.line','search_read',
        [[['move_id.move_type','=','out_invoice'],
          ['move_id.state','=','posted'],
          ['move_id.invoice_date','>=',start30],
          ['product_id','!=',False]]],
        {'fields':['product_id','quantity','price_subtotal'],'limit':5000})
    by_prod = {}
    for l in lines:
        p = l.get('product_id')
        if not p: continue
        pid = p[0]
        by_prod.setdefault(pid, {'name':p[1],'units':0,'ca':0})
        by_prod[pid]['units'] += l.get('quantity') or 0
        by_prod[pid]['ca'] += l.get('price_subtotal') or 0
    sorted_p = sorted(by_prod.items(), key=lambda x:-x[1]['ca'])
    data['products_top'] = [
        {'sku':f'P{pid}','name':info['name'][:40],'units':int(info['units']),
         'ca':round(info['ca']),'delta':0.0}
        for pid,info in sorted_p[:5]
    ]
    data['products_flop'] = [
        {'sku':f'P{pid}','name':info['name'][:40],'rot':round(info['units']/30,2),
         'stock':0,'act':'à analyser'}
        for pid,info in sorted_p[-5:] if info['units']>0
    ]
except Exception as e:
    data['products_error'] = str(e)

with open('cockpit_data.json','w',encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[OK] cockpit_data.json · {len(data.get('orders',[]))} orders · {len(data.get('stores',[]))} stores · {len(data.get('products_top',[]))} top products")
