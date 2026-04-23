"""
Diagnostic profond :
1. Pourquoi la route Buy est inactive ?
2. Produits qui devraient etre Buy mais qui n'ont plus de route operationnelle
3. MO recents : comment ont-ils ete crees alors que 1 seul template a la route Manufacture ?
"""
import xmlrpc.client
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})


ROUTE_MANUFACTURE = 6
ROUTE_BUY = 5

# === 1) Etat route Buy + rules associées ===
print("=== ROUTE BUY (id=5) ===", flush=True)
route_buy = call("stock.route", "read", [[ROUTE_BUY],
                 ["id", "name", "active", "product_selectable", "product_categ_selectable", "warehouse_selectable", "rule_ids", "company_id"]],
                 {"context": {"active_test": False}})
print(json.dumps(route_buy, indent=2, default=str, ensure_ascii=False), flush=True)

if route_buy and route_buy[0].get("rule_ids"):
    rules = call("stock.rule", "read", [route_buy[0]["rule_ids"],
                                          ["id", "name", "action", "active", "location_dest_id", "picking_type_id", "company_id"]],
                 {"context": {"active_test": False}})
    print(f"\nRules de la route Buy :", flush=True)
    for r in rules:
        print(f"  id={r['id']} | {r['name']} | action={r['action']} | active={r['active']} | dest={r.get('location_dest_id')}", flush=True)

# === 2) Mail.message sur la route Buy pour voir qui l'a desactivee ===
print("\n=== Message history sur route_buy ===", flush=True)
msgs = call("mail.message", "search_read",
            [[("model", "=", "stock.route"), ("res_id", "=", ROUTE_BUY)]],
            {"fields": ["id", "date", "author_id", "body", "subject", "tracking_value_ids"],
             "order": "date desc", "limit": 20})
for msg in msgs:
    body = (msg.get("body") or "")[:300].replace("<", "[").replace(">", "]")
    print(f"  {msg['date']} | {msg['author_id']} | {body}", flush=True)
    if msg.get("tracking_value_ids"):
        tvs = call("mail.tracking.value", "read", [msg["tracking_value_ids"], ["field_desc", "old_value_char", "new_value_char", "old_value_integer", "new_value_integer"]])
        for tv in tvs:
            print(f"    track: {tv}", flush=True)

# === 3) Mail.message sur route Manufacture ===
print("\n=== Message history sur route_manufacture (id=6) ===", flush=True)
msgs6 = call("mail.message", "search_read",
            [[("model", "=", "stock.route"), ("res_id", "=", ROUTE_MANUFACTURE)]],
            {"fields": ["id", "date", "author_id", "body", "subject", "tracking_value_ids"],
             "order": "date desc", "limit": 10})
for msg in msgs6:
    body = (msg.get("body") or "")[:300].replace("<", "[").replace(">", "]")
    print(f"  {msg['date']} | {msg['author_id']} | {body}", flush=True)

# === 4) Produits avec fournisseur MAIS sans route operationnelle (ni buy active, ni manufacture) ===
# Focus sur templates ayant seller_ids (= achat normal)
print("\n=== Templates avec seller_ids : leurs routes ===", flush=True)
tpl_with_seller = call("product.template", "search_count", [[("seller_ids", "!=", False)]])
print(f"Total templates avec seller : {tpl_with_seller}", flush=True)

# Sample 30 pour voir quelles routes ils ont
sample_tpl_ids = call("product.template", "search", [[("seller_ids", "!=", False)]], {"limit": 500})
sample_tpls = call("product.template", "read", [sample_tpl_ids,
                    ["id", "default_code", "name", "route_ids", "purchase_ok"]])
from collections import Counter
route_usage = Counter()
for t in sample_tpls:
    routes_tuple = tuple(sorted(t.get("route_ids") or []))
    route_usage[routes_tuple] += 1
print(f"\nDistribution des route_ids sur templates avec seller (500 sample) :", flush=True)
for routes_tuple, cnt in route_usage.most_common(20):
    # resolve names
    if routes_tuple:
        names = call("stock.route", "read", [list(routes_tuple), ["id", "name"]], {"context": {"active_test": False}})
        name_str = ", ".join(f"{n['id']}:{n['name']}" for n in names)
    else:
        name_str = "(aucune)"
    print(f"  {cnt}x {routes_tuple} : {name_str}", flush=True)

# === 5) MO recents (2026-04-23) : tracer leur source ===
print("\n=== MO d'aujourd'hui 2026-04-23 : qui/comment ===", flush=True)
mo_ids_today = call("mrp.production", "search",
                     [[("create_date", ">=", "2026-04-23 00:00:00")]],
                     {"order": "create_date desc"})
print(f"MO crees aujourd'hui : {len(mo_ids_today)}", flush=True)

if mo_ids_today:
    mos = call("mrp.production", "read",
               [mo_ids_today, ["id", "name", "product_id", "state", "create_date", "origin", "product_qty", "create_uid", "orderpoint_id", "procurement_group_id"]])
    print("\nDetail MO du jour :", flush=True)
    for mo in mos:
        print(f"  {mo['name']} | {mo['product_id'][1] if mo['product_id'] else '?'} | create={mo['create_date']} | user={mo.get('create_uid')} | OP={mo.get('orderpoint_id')}", flush=True)

    # Les orderpoints qui ont genere ces MO
    op_ids = list({mo["orderpoint_id"][0] for mo in mos if mo.get("orderpoint_id")})
    print(f"\n{len(op_ids)} orderpoints distincts ont genere des MO aujourd'hui", flush=True)
    if op_ids:
        ops = call("stock.warehouse.orderpoint", "read", [op_ids,
                  ["id", "name", "product_id", "route_id", "warehouse_id"]])
        for op in ops:
            print(f"  OP {op['name']} | prod={op['product_id'][1] if op['product_id'] else '?'} | route={op.get('route_id')}", flush=True)

        # Regarder les route_ids sur les products de ces OP
        prod_ids = list({op["product_id"][0] for op in ops if op.get("product_id")})
        if prod_ids:
            prods = call("product.product", "read", [prod_ids,
                  ["id", "default_code", "name", "route_ids", "product_tmpl_id"]])
            print(f"\nProduits des OP ({len(prods)}) :", flush=True)
            for p in prods:
                route_names = []
                if p.get("route_ids"):
                    rn = call("stock.route", "read", [p["route_ids"], ["id", "name", "active"]], {"context": {"active_test": False}})
                    route_names = [f"{r['id']}:{r['name']}(act={r['active']})" for r in rn]
                print(f"  {p['id']} | {p['default_code']} | product.product routes={route_names}", flush=True)
                # tpl routes
                tpl_data = call("product.template", "read", [[p["product_tmpl_id"][0]], ["route_ids"]])[0]
                if tpl_data.get("route_ids"):
                    trn = call("stock.route", "read", [tpl_data["route_ids"], ["id", "name", "active"]], {"context": {"active_test": False}})
                    tpl_routes = [f"{r['id']}:{r['name']}(act={r['active']})" for r in trn]
                else:
                    tpl_routes = []
                print(f"       tpl routes={tpl_routes}", flush=True)
