"""
Diagnostic elargi : route Manufacture via product.template ET product.product ET orderpoints.

Nicolas signale que des produits basculent en "Fabriquer" au lieu de "Acheter"
et que des MO ont ete supprimees ce matin.
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


# === Routes disponibles ===
print("=== ROUTES ===", flush=True)
routes = call("stock.route", "search_read",
              [[]],
              {"fields": ["id", "name", "active", "product_selectable", "sequence"],
               "context": {"active_test": False}})
for r in routes:
    print(f"  id={r['id']} | {r['name']} | active={r['active']} | prod_sel={r['product_selectable']}", flush=True)

ROUTE_MANUFACTURE = 6

# Chercher Buy
buy_candidates = [r for r in routes if "buy" in r["name"].lower() or "acheter" in r["name"].lower() or "achat" in r["name"].lower()]
print(f"\nBuy candidates : {buy_candidates}", flush=True)

# Via stock.rule action=buy
rules_buy = call("stock.rule", "search_read",
                 [[("action", "=", "buy")]],
                 {"fields": ["id", "name", "route_id", "active"],
                  "context": {"active_test": False}})
print(f"\nRules action=buy : {rules_buy}", flush=True)

route_buy_id = None
if rules_buy:
    route_buy_id = rules_buy[0]["route_id"][0] if rules_buy[0].get("route_id") else None
print(f"ROUTE_BUY detectee = {route_buy_id}", flush=True)

# === 1) Templates avec route Manufacture ===
print("\n=== TEMPLATES route Manufacture ===", flush=True)
tpl_ids = call("product.template", "search", [[("route_ids", "in", [ROUTE_MANUFACTURE])]])
print(f"Nombre : {len(tpl_ids)}", flush=True)
if tpl_ids:
    tpls = call("product.template", "read",
                [tpl_ids, ["id", "default_code", "name", "route_ids", "seller_ids", "bom_ids", "bom_count", "purchase_ok"]])
    for t in tpls:
        print(f"  {t['id']} | {t.get('default_code')} | {t['name'][:60]} | bom_count={t.get('bom_count')} | sellers={len(t.get('seller_ids') or [])}", flush=True)

# === 2) Products (product.product) avec route Manufacture ===
print("\n=== PRODUCTS route Manufacture (product.product) ===", flush=True)
prod_ids = call("product.product", "search", [[("route_ids", "in", [ROUTE_MANUFACTURE])]])
print(f"Nombre product.product : {len(prod_ids)}", flush=True)
if prod_ids:
    prods = call("product.product", "read",
                 [prod_ids, ["id", "default_code", "name", "route_ids", "product_tmpl_id", "seller_ids"]])
    for p in prods[:30]:
        print(f"  {p['id']} | {p.get('default_code')} | {p['name'][:60]} | tpl={p['product_tmpl_id']} | sellers={len(p.get('seller_ids') or [])}", flush=True)

# === 3) Orderpoints route Manufacture ===
print("\n=== ORDERPOINTS route=Manufacture ===", flush=True)
op_ids = call("stock.warehouse.orderpoint", "search", [[("route_id", "=", ROUTE_MANUFACTURE)]])
print(f"Nombre : {len(op_ids)}", flush=True)
if op_ids:
    ops = call("stock.warehouse.orderpoint", "read",
               [op_ids, ["id", "name", "product_id", "route_id", "warehouse_id"]])
    for o in ops[:20]:
        print(f"  {o['id']} | {o['name']} | prod={o['product_id'][1] if o['product_id'] else '?'}", flush=True)

# === 4) Categories route Manufacture ===
print("\n=== CATEGORIES route Manufacture ===", flush=True)
cat_ids = call("product.category", "search", [[("route_ids", "in", [ROUTE_MANUFACTURE])]])
print(f"Nombre : {len(cat_ids)}", flush=True)
if cat_ids:
    cats = call("product.category", "read", [cat_ids, ["id", "name", "route_ids"]])
    for c in cats:
        print(f"  {c['id']} | {c['name']}", flush=True)

# === 5) MO créés depuis hier (2026-04-22) ===
print("\n=== MO crees depuis 2026-04-22 ===", flush=True)
mo_ids = call("mrp.production", "search",
              [[("create_date", ">=", "2026-04-22 00:00:00")]],
              {"order": "create_date desc", "limit": 200})
print(f"Nombre : {len(mo_ids)}", flush=True)
if mo_ids:
    mos = call("mrp.production", "read",
               [mo_ids, ["id", "name", "product_id", "state", "create_date", "origin", "product_qty"]])
    print("Par etat :", flush=True)
    from collections import Counter
    by_state = Counter([mo["state"] for mo in mos])
    print(f"  {dict(by_state)}", flush=True)
    print("Par produit (top 20) :", flush=True)
    by_prod = Counter([mo["product_id"][1] if mo["product_id"] else "?" for mo in mos])
    for n, c in by_prod.most_common(20):
        print(f"  {c}x {n}", flush=True)
    print("Sample (10 recents) :", flush=True)
    for mo in mos[:10]:
        print(f"  {mo['name']} | {mo['product_id'][1] if mo['product_id'] else '?'} | qty={mo['product_qty']} | state={mo['state']} | create={mo['create_date']} | origin={mo['origin']}", flush=True)

# === 6) MO toutes dates (state draft/confirmed) — ce qui est vivant ===
print("\n=== MO vivants (draft/confirmed/progress) ===", flush=True)
mo_live = call("mrp.production", "search_count",
               [[("state", "in", ["draft", "confirmed", "progress"])]])
print(f"Nombre MO non termines : {mo_live}", flush=True)
if mo_live:
    mo_live_ids = call("mrp.production", "search",
                       [[("state", "in", ["draft", "confirmed", "progress"])]],
                       {"order": "create_date desc", "limit": 500})
    mos_live = call("mrp.production", "read",
                    [mo_live_ids, ["id", "name", "product_id", "state", "create_date", "origin", "product_qty"]])
    from collections import Counter
    print("Par produit top 20 :", flush=True)
    by_prod = Counter([mo["product_id"][1] if mo["product_id"] else "?" for mo in mos_live])
    for n, c in by_prod.most_common(20):
        print(f"  {c}x {n}", flush=True)
    print("Par origin prefix :", flush=True)
    by_origin = Counter([((mo["origin"] or "?").split("/")[0]) for mo in mos_live])
    print(f"  {dict(by_origin)}", flush=True)

# Sauvegarde
out = {
    "route_manufacture_id": ROUTE_MANUFACTURE,
    "route_buy_id": route_buy_id,
    "routes_all": routes,
    "tpl_ids_manufacture": tpl_ids,
    "prod_ids_manufacture": prod_ids,
    "op_ids_manufacture": op_ids,
    "cat_ids_manufacture": cat_ids,
    "mo_since_2026_04_22": len(mo_ids) if mo_ids else 0,
    "mo_live_count": mo_live,
}
with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423/diag_wide.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str, ensure_ascii=False)
print("\nDiag ecrit.", flush=True)
