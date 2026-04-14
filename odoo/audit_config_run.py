"""Audit config Odoo Teatower - read-only, XML-RPC.
Produit un JSON riche par domaine, consommé ensuite pour rédiger le rapport MD.
"""
import xmlrpc.client, json, sys, traceback, datetime, collections

URL  = "https://tea-tree.odoo.com"
DB   = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD  = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, USER, PWD, {})
print("uid=", uid, file=sys.stderr)
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

def rpc(model, method, args, kwargs=None):
    return models.execute_kw(DB, uid, PWD, model, method, args, kwargs or {})

out = {}

def safe(name, fn):
    try:
        t0 = datetime.datetime.now()
        r = fn()
        out[name] = r
        print(f"[OK] {name} ({(datetime.datetime.now()-t0).total_seconds():.1f}s)", file=sys.stderr)
    except Exception as e:
        out[name] = {"_error": str(e), "_tb": traceback.format_exc()[-600:]}
        print(f"[ERR] {name}: {e}", file=sys.stderr)

# 1. Warehouses / routes / picking types
def wh():
    whs = rpc('stock.warehouse','search_read',[[]],
        {'fields':['name','code','reception_steps','delivery_steps','lot_stock_id','in_type_id','out_type_id','active','company_id']})
    routes = rpc('stock.route','search_read',[[]],{'fields':['name','active','warehouse_ids','product_selectable','product_categ_selectable','sequence']})
    ptypes = rpc('stock.picking.type','search_read',[[]],
        {'fields':['name','code','sequence_code','default_location_src_id','default_location_dest_id','reservation_method','use_create_lots','use_existing_lots','warehouse_id','active','show_operations']})
    # Allow negative by category
    cats = rpc('product.category','search_read',[[]],
        {'fields':['complete_name','property_cost_method','property_valuation','property_stock_valuation_account_id','removal_strategy_id']})
    return {'warehouses':whs,'routes':routes,'picking_types':ptypes,'categories':cats}
safe('warehouses_routes', wh)

# 2. Orderpoints
def op():
    ops = rpc('stock.warehouse.orderpoint','search_read',[[]],
        {'fields':['product_id','location_id','product_min_qty','product_max_qty','qty_multiple','trigger','route_id','warehouse_id','company_id','active']})
    count_all = len(ops)
    # orphans: product inactive
    pids = list({o['product_id'][0] for o in ops if o['product_id']})
    active_map = {}
    for i in range(0, len(pids), 500):
        chunk = pids[i:i+500]
        for p in rpc('product.product','search_read',[[['id','in',chunk]]],{'fields':['id','active','default_code','name','purchase_ok','seller_ids','standard_price']}):
            active_map[p['id']] = p
    orphan_inactive = [o for o in ops if not active_map.get(o['product_id'][0],{}).get('active',True)]
    # doublons
    seen = collections.Counter()
    for o in ops:
        key = (o['product_id'][0], o['location_id'][0] if o['location_id'] else 0)
        seen[key]+=1
    dup = [k for k,v in seen.items() if v>1]
    by_loc = collections.Counter(o['location_id'][1] if o['location_id'] else 'NONE' for o in ops)
    mto_routes = rpc('stock.route','search_count',[[['name','ilike','make to order']]])
    return {'total':count_all,'orphans_inactive':len(orphan_inactive),
            'doublons':len(dup),'by_location':dict(by_loc.most_common(30)),
            'mto_route_count':mto_routes,
            'sample_orphan':[{'op':o['id'],'pid':o['product_id']} for o in orphan_inactive[:10]]}
safe('orderpoints', op)

# 3. Produits
def prod():
    tpl_total = rpc('product.template','search_count',[[]])
    tpl_active = rpc('product.template','search_count',[[['active','=',True]]])
    prod_total = rpc('product.product','search_count',[[]])
    prod_active = rpc('product.product','search_count',[[['active','=',True]]])
    # type distribution
    tpls = rpc('product.template','search_read',[[['active','=',True]]],
        {'fields':['id','name','default_code','type','is_storable','purchase_ok','sale_ok','standard_price','list_price','taxes_id','categ_id','seller_ids']})
    by_type = collections.Counter((t.get('type'), t.get('is_storable')) for t in tpls)
    no_supplier = [t for t in tpls if t.get('purchase_ok') and not t.get('seller_ids')]
    zero_cost = [t for t in tpls if t.get('sale_ok') and (t.get('standard_price') or 0)==0]
    no_barcode = rpc('product.product','search_count',[[['active','=',True],['barcode','=',False]]])
    no_default_code = rpc('product.template','search_count',[[['active','=',True],['default_code','=',False]]])
    # doublons default_code
    codes = collections.Counter(t['default_code'] for t in tpls if t.get('default_code'))
    dup_codes = [c for c,n in codes.items() if n>1]
    # variantes
    with_variants = rpc('product.template','search_count',[[['attribute_line_ids','!=',False]]])
    return {'tpl_total':tpl_total,'tpl_active':tpl_active,
            'prod_total':prod_total,'prod_active':prod_active,
            'by_type':{f"{k[0]}|storable={k[1]}":v for k,v in by_type.items()},
            'no_supplier':len(no_supplier),'zero_cost':len(zero_cost),
            'no_barcode':no_barcode,'no_default_code':no_default_code,
            'dup_default_code':len(dup_codes),'sample_dup_codes':dup_codes[:10],
            'with_variants':with_variants,
            'sample_no_supplier':[t['default_code'] for t in no_supplier[:20]]}
safe('products', prod)

# 4. BoM / MRP
def mrp():
    try:
        boms = rpc('mrp.bom','search_read',[[]],{'fields':['product_tmpl_id','product_id','type','active','bom_line_ids']})
        by_type = collections.Counter(b['type'] for b in boms)
        # bom with inactive components
        all_line_ids = [lid for b in boms for lid in b.get('bom_line_ids',[])]
        bad_boms = 0
        if all_line_ids:
            lines = rpc('mrp.bom.line','search_read',[[['id','in',all_line_ids]]],{'fields':['product_id','bom_id']})
            line_pids = list({l['product_id'][0] for l in lines if l['product_id']})
            active_map = {}
            for i in range(0,len(line_pids),500):
                for p in rpc('product.product','search_read',[[['id','in',line_pids[i:i+500]]]],{'fields':['id','active']}):
                    active_map[p['id']]=p['active']
            bad_boms = len({l['bom_id'][0] for l in lines if not active_map.get(l['product_id'][0],True)})
        mo_stale = rpc('mrp.production','search_count',[[['state','in',['confirmed','progress','to_close']],['create_date','<','2026-03-15']]])
        mo_total = rpc('mrp.production','search_count',[[]])
        return {'bom_total':len(boms),'by_type':dict(by_type),'bom_with_inactive_comp':bad_boms,
                'mo_total':mo_total,'mo_stale_30d':mo_stale}
    except Exception as e:
        return {"_error":str(e)}
safe('mrp', mrp)

# 5. Ventes
def sales():
    total = rpc('sale.order','search_count',[[]])
    draft = rpc('sale.order','search_count',[[['state','=','draft']]])
    sent = rpc('sale.order','search_count',[[['state','=','sent']]])
    cancel = rpc('sale.order','search_count',[[['state','=','cancel']]])
    done_12mo = rpc('sale.order','search_count',[[['state','in',['sale','done']],['date_order','>','2025-04-14']]])
    no_ref_gms = rpc('sale.order','search_count',[[['state','in',['sale','done']],['client_order_ref','in',[False,'']]]])
    pricelists = rpc('product.pricelist','search_read',[[]],{'fields':['name','active','currency_id','country_group_ids']})
    payterms = rpc('account.payment.term','search_read',[[]],{'fields':['name','active']})
    carriers = rpc('delivery.carrier','search_read',[[]],{'fields':['name','delivery_type','active']})
    return {'total':total,'draft':draft,'sent':sent,'cancel':cancel,'done_12mo':done_12mo,
            'no_client_order_ref':no_ref_gms,
            'pricelists':len(pricelists),'pricelists_active':sum(1 for p in pricelists if p['active']),
            'payterms':len(payterms),'carriers':len(carriers),
            'pricelist_names':[p['name'] for p in pricelists]}
safe('sales', sales)

# 6. Achats
def purch():
    po_total = rpc('purchase.order','search_count',[[]])
    rfq_dormant = rpc('purchase.order','search_count',[[['state','in',['draft','sent']],['create_date','<','2026-03-15']]])
    po_done_12mo = rpc('purchase.order','search_count',[[['state','in',['purchase','done']],['date_order','>','2025-04-14']]])
    supinfo_total = rpc('product.supplierinfo','search_count',[[]])
    supinfo_no_delay = rpc('product.supplierinfo','search_count',[[['delay','=',0]]])
    return {'po_total':po_total,'rfq_dormant_30d':rfq_dormant,'po_done_12mo':po_done_12mo,
            'supplierinfo_total':supinfo_total,'supplierinfo_delay_0':supinfo_no_delay}
safe('purchase', purch)

# 7. Compta
def acc():
    journals = rpc('account.journal','search_read',[[]],{'fields':['name','code','type','active']})
    taxes = rpc('account.tax','search_read',[[]],{'fields':['name','amount','type_tax_use','active','country_id','tax_group_id']})
    taxes_be = [t for t in taxes if t['active']]
    moves_post = rpc('account.move','search_count',[[['state','=','posted']]])
    open_invoices = rpc('account.move','search_count',[[['move_type','=','out_invoice'],['state','=','posted'],['payment_state','in',['not_paid','partial']]]])
    open_inv_60d = rpc('account.move','search_count',[[['move_type','=','out_invoice'],['state','=','posted'],['payment_state','in',['not_paid','partial']],['invoice_date','<','2026-02-14']]])
    try:
        analytic_plans = rpc('account.analytic.plan','search_read',[[]],{'fields':['name','company_id']})
    except Exception:
        analytic_plans = []
    return {'journals':len(journals),
            'journals_detail':[{'code':j['code'],'type':j['type']} for j in journals],
            'taxes_active':len(taxes_be),
            'taxes_sample':[{'name':t['name'],'amount':t['amount'],'use':t['type_tax_use']} for t in taxes_be[:30]],
            'moves_posted':moves_post,
            'open_invoices':open_invoices,'open_invoices_over_60d':open_inv_60d,
            'analytic_plans':len(analytic_plans)}
safe('accounting', acc)

# 8. ir.cron + ir.mail_server
def auto():
    crons = rpc('ir.cron','search_read',[[]],{'fields':['name','active','interval_number','interval_type','nextcall','lastcall','model_id']})
    active_crons = [c for c in crons if c['active']]
    try:
        basea = rpc('base.automation','search_count',[[]])
    except Exception: basea = None
    mail_srv = rpc('ir.mail_server','search_read',[[]],{'fields':['name','active','smtp_host','smtp_port']})
    try:
        fetchmail = rpc('fetchmail.server','search_read',[[]],{'fields':['name','state','server']})
    except Exception: fetchmail = []
    return {'cron_total':len(crons),'cron_active':len(active_crons),
            'cron_list':[{'name':c['name'],'every':f"{c['interval_number']} {c['interval_type']}",
                          'nextcall':str(c['nextcall']),'active':c['active']} for c in active_crons],
            'base_automation':basea,
            'mail_servers':mail_srv,'fetchmail':fetchmail}
safe('automations', auto)

# 9. Séquences
def seq():
    seqs = rpc('ir.sequence','search_read',[[]],{'fields':['name','code','prefix','padding','implementation','number_next_actual','active']})
    # collisions prefix
    prefs = collections.Counter(s['prefix'] for s in seqs if s['prefix'])
    dup_prefix = [p for p,n in prefs.items() if n>1]
    return {'total':len(seqs),'dup_prefix':dup_prefix,
            'sample':[{'code':s['code'],'prefix':s['prefix'],'pad':s['padding'],'impl':s['implementation']} for s in seqs if s['code'] in ('sale.order','account.move','purchase.order','stock.picking','account.payment')]}
safe('sequences', seq)

# 10. Users
def usr():
    users = rpc('res.users','search_read',[[]],{'fields':['name','login','active','company_ids','groups_id','share']})
    internal = [u for u in users if not u['share']]
    portal = [u for u in users if u['share']]
    companies = rpc('res.company','search_read',[[]],{'fields':['name','currency_id','country_id']})
    return {'users_total':len(users),'internal':len(internal),'portal':len(portal),
            'active_internal':sum(1 for u in internal if u['active']),
            'companies':len(companies),
            'internal_list':[{'name':u['name'],'login':u['login'],'active':u['active'],'groups':len(u['groups_id'])} for u in internal]}
safe('users', usr)

# 11. Modules installés
def mods():
    try:
        ms = rpc('ir.module.module','search_read',[[['state','=','installed']]],{'fields':['name','shortdesc','author','application']})
        apps = [m for m in ms if m['application']]
        shopify = [m for m in ms if 'shopify' in m['name'].lower()]
        amazon = [m for m in ms if 'amazon' in m['name'].lower()]
        return {'installed':len(ms),'apps':len(apps),
                'shopify':[m['name'] for m in shopify],'amazon':[m['name'] for m in amazon],
                'apps_list':[m['name'] for m in apps]}
    except Exception as e: return {"_error":str(e)}
safe('modules', mods)

# 12. Data quality
def dq():
    partners_total = rpc('res.partner','search_count',[[]])
    partners_no_email = rpc('res.partner','search_count',[[['customer_rank','>',0],['email','=',False],['phone','=',False],['mobile','=',False]]])
    # duplicates VAT
    vats = rpc('res.partner','read_group',[[['vat','!=',False],['parent_id','=',False]],['vat'],['vat']],{'lazy':False})
    dup_vat = [v for v in vats if v['__count']>1]
    emails = rpc('res.partner','read_group',[[['email','!=',False],['parent_id','=',False]],['email'],['email']],{'lazy':False})
    dup_email = [e for e in emails if e['__count']>1]
    return {'partners_total':partners_total,'customers_no_contact':partners_no_email,
            'dup_vat':len(dup_vat),'dup_email':len(dup_email),
            'sample_dup_vat':[{'vat':v['vat'],'count':v['__count']} for v in dup_vat[:10]],
            'sample_dup_email':[{'email':e['email'],'count':e['__count']} for e in dup_email[:10]]}
safe('data_quality', dq)

# Save
with open('odoo/audit_config_data.json','w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
print("DONE")
