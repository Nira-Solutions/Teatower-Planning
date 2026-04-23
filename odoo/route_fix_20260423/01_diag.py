"""
Diagnostic route Manufacture sur product.template — 2026-04-23

Objectif : lister tous les templates qui ont encore la route Manufacture (id=6)
et identifier ceux qui devraient en fait être en route Buy.

Logique métier :
- Produit avec fournisseur (seller_ids) ET sans BoM active = anomalie (devrait être Buy)
- Produit avec BoM active = légitimement Manufacture (coffrets, assortiments, C0200)
- default_code I0xxx/V0xxx = thés (achat Kirchner typiquement)
- default_code C0xxx = coffrets/composants (parfois fabriqués, parfois achetés)
- default_code A0xxx = accessoires (achat)
- default_code R0xxx = matières premières (achat)
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
ROUTE_BUY = None  # à résoudre
KEEP_TMPL = 10485  # C0200 — legit fabrique

# 1) Trouver la route Buy (id)
buy_routes = call(
    "stock.route", "search_read",
    [[("name", "in", ["Buy", "Acheter", "Purchase"])]],
    {"fields": ["id", "name", "active"]},
)
print(f"Routes Buy trouvees : {buy_routes}", flush=True)
ROUTE_BUY = buy_routes[0]["id"] if buy_routes else None

# 2) Tous les templates avec route Manufacture
tpl_ids = call("product.template", "search", [[("route_ids", "in", [ROUTE_MANUFACTURE])]])
print(f"\nTotal templates avec route Manufacture : {len(tpl_ids)}", flush=True)

if not tpl_ids:
    print("Aucun template concerne. Verifions en amont (orderpoints / MO recents).", flush=True)
else:
    tpls = call(
        "product.template", "read",
        [tpl_ids, [
            "id", "default_code", "name", "route_ids", "seller_ids",
            "bom_ids", "bom_count", "purchase_ok", "sale_ok",
            "product_tmpl_id", "type", "detailed_type",
        ]],
    )

    # BoMs actives
    all_bom_ids = []
    for t in tpls:
        all_bom_ids += t.get("bom_ids") or []
    active_boms = set()
    if all_bom_ids:
        boms = call("mrp.bom", "read", [list(set(all_bom_ids)), ["id", "active", "product_tmpl_id"]])
        active_boms = {b["id"] for b in boms if b.get("active")}

    # Classification
    anomalies = []  # a des fournisseurs, pas de BoM active -> devrait etre Buy
    legit_mo = []   # a une BoM active -> legit Manufacture
    orphans = []    # ni fournisseur ni BoM active -> indefini

    for t in tpls:
        has_seller = bool(t.get("seller_ids"))
        has_active_bom = any(b in active_boms for b in (t.get("bom_ids") or []))
        rec = {
            "id": t["id"],
            "default_code": t.get("default_code"),
            "name": t.get("name"),
            "route_ids": t.get("route_ids"),
            "has_seller": has_seller,
            "has_bom": bool(t.get("bom_ids")),
            "has_active_bom": has_active_bom,
            "bom_count": t.get("bom_count"),
            "purchase_ok": t.get("purchase_ok"),
            "sale_ok": t.get("sale_ok"),
            "type": t.get("type"),
            "detailed_type": t.get("detailed_type"),
        }
        if has_active_bom:
            legit_mo.append(rec)
        elif has_seller:
            anomalies.append(rec)
        else:
            orphans.append(rec)

    print(f"\n=== Classification ===", flush=True)
    print(f"  Legit MO (BoM active)       : {len(legit_mo)}", flush=True)
    print(f"  ANOMALIES (seller sans BoM) : {len(anomalies)}", flush=True)
    print(f"  Orphans (ni seller ni BoM)  : {len(orphans)}", flush=True)

    print(f"\n=== Sample Legit MO (5) ===", flush=True)
    for r in legit_mo[:5]:
        print(f"  {r['id']} | {r['default_code']} | {r['name'][:60]} | bom_count={r['bom_count']}", flush=True)

    print(f"\n=== Sample ANOMALIES (20) ===", flush=True)
    for r in anomalies[:20]:
        print(f"  {r['id']} | {r['default_code']} | {r['name'][:60]} | purchase_ok={r['purchase_ok']}", flush=True)

    print(f"\n=== Sample Orphans (10) ===", flush=True)
    for r in orphans[:10]:
        print(f"  {r['id']} | {r['default_code']} | {r['name'][:60]}", flush=True)

    out = {
        "route_buy_id": ROUTE_BUY,
        "route_manufacture_id": ROUTE_MANUFACTURE,
        "total_tpl_with_manufacture": len(tpls),
        "legit_mo": legit_mo,
        "anomalies": anomalies,
        "orphans": orphans,
    }
    with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423/diag.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str, ensure_ascii=False)
    print("\nDiag ecrit dans route_fix_20260423/diag.json", flush=True)

# 3) Check orderpoints avec route_id=6 (autre vecteur)
op_count = call("stock.warehouse.orderpoint", "search_count", [[("route_id", "=", ROUTE_MANUFACTURE)]])
print(f"\nOrderpoints avec route_id=Manufacture : {op_count}", flush=True)

# 4) Check catégories
cat_ids = call("product.category", "search", [[("route_ids", "in", [ROUTE_MANUFACTURE])]])
if cat_ids:
    cats = call("product.category", "read", [cat_ids, ["id", "name", "route_ids"]])
    print(f"\nCategories avec route Manufacture : {cats}", flush=True)
else:
    print("\nAucune categorie avec route Manufacture.", flush=True)

# 5) MO recents (depuis 2026-04-22)
recent_mo = call("mrp.production", "search_count", [[("create_date", ">=", "2026-04-22 00:00:00")]])
print(f"\nMO crees depuis 2026-04-22 : {recent_mo}", flush=True)
if recent_mo:
    mo_ids = call("mrp.production", "search",
                  [[("create_date", ">=", "2026-04-22 00:00:00")]],
                  {"order": "create_date desc", "limit": 50})
    mos = call("mrp.production", "read", [mo_ids,
              ["id", "name", "product_id", "state", "create_date", "origin", "product_qty"]])
    print(f"Sample MO recents (10) :", flush=True)
    for mo in mos[:10]:
        print(f"  {mo['name']} | {mo['product_id'][1] if mo['product_id'] else '?'} | qty={mo['product_qty']} | state={mo['state']} | create={mo['create_date']} | origin={mo['origin']}", flush=True)
