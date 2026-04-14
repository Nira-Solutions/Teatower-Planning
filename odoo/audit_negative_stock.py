"""Audit stocks negatifs Odoo Teatower."""
import xmlrpc.client
import json
from collections import defaultdict

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

print(f"UID: {uid}")

# 1) Récupérer toutes les locations internes
internal_locs = call("stock.location", "search_read",
    [[("usage", "=", "internal")]],
    {"fields": ["id", "complete_name", "warehouse_id"]})
internal_ids = [l["id"] for l in internal_locs]
loc_by_id = {l["id"]: l for l in internal_locs}
print(f"Locations internes: {len(internal_ids)}")

# 2) Quants négatifs sur locations internes
neg_quants = call("stock.quant", "search_read",
    [[("location_id", "in", internal_ids), ("quantity", "<", 0)]],
    {"fields": ["id", "product_id", "location_id", "quantity", "reserved_quantity",
                "available_quantity", "in_date"]})
print(f"Quants negatifs: {len(neg_quants)}")

# Extraire produits uniques
prod_ids = list({q["product_id"][0] for q in neg_quants})
prods = call("product.product", "read", [prod_ids],
    {"fields": ["id", "default_code", "name", "standard_price", "list_price",
                "qty_available", "virtual_available"]})
prod_by_id = {p["id"]: p for p in prods}

# Stats globales
total_neg_qty = sum(q["quantity"] for q in neg_quants)
locs_concerned = {q["location_id"][0] for q in neg_quants}
prods_concerned = {q["product_id"][0] for q in neg_quants}
total_value = sum(q["quantity"] * prod_by_id[q["product_id"][0]].get("standard_price", 0)
                  for q in neg_quants)

print(f"\n=== STATS GLOBALES ===")
print(f"Quants negatifs: {len(neg_quants)}")
print(f"Produits concernes: {len(prods_concerned)}")
print(f"Locations concernees: {len(locs_concerned)}")
print(f"Total qty negative: {total_neg_qty:.2f}")
print(f"Valeur totale negative (cout std): {total_value:.2f} EUR")

# Top 20 par qty négative (somme par produit toutes locations confondues)
by_prod = defaultdict(lambda: {"qty": 0, "locs": []})
for q in neg_quants:
    pid = q["product_id"][0]
    by_prod[pid]["qty"] += q["quantity"]
    by_prod[pid]["locs"].append((q["location_id"][1], q["quantity"]))

top20 = sorted(by_prod.items(), key=lambda x: x[1]["qty"])[:20]

print(f"\n=== TOP 20 PRODUITS LES PLUS NEGATIFS ===")
top20_data = []
for pid, info in top20:
    p = prod_by_id[pid]
    val = info["qty"] * p.get("standard_price", 0)
    print(f"[{p.get('default_code') or '-'}] {p['name'][:50]:50} | qty={info['qty']:.1f} | val={val:.2f} | locs={len(info['locs'])}")
    top20_data.append({
        "default_code": p.get("default_code"),
        "name": p["name"],
        "qty_neg": info["qty"],
        "value_neg": val,
        "nb_locs": len(info["locs"]),
        "locs": info["locs"],
        "product_id": pid,
    })

# Détail par location pour chaque quant
print(f"\n=== REPARTITION PAR LOCATION ===")
by_loc = defaultdict(lambda: {"qty": 0, "n": 0})
for q in neg_quants:
    lid = q["location_id"][0]
    by_loc[lid]["qty"] += q["quantity"]
    by_loc[lid]["n"] += 1
for lid, info in sorted(by_loc.items(), key=lambda x: x[1]["qty"]):
    lname = loc_by_id[lid]["complete_name"]
    print(f"{lname:60} | n={info['n']:4} | qty={info['qty']:.1f}")

# Sauve résultat
out = {
    "stats": {
        "n_quants": len(neg_quants),
        "n_products": len(prods_concerned),
        "n_locations": len(locs_concerned),
        "total_qty_neg": total_neg_qty,
        "total_value_neg": total_value,
    },
    "top20": top20_data,
    "by_loc": {loc_by_id[lid]["complete_name"]: info for lid, info in by_loc.items()},
}
with open("C:/Users/FlowUP/Downloads/Claude/Claude/Teatower/odoo/audit_neg_stats.json", "w", encoding="utf-8") as f:
    json.dump(out, f, default=str, indent=2, ensure_ascii=False)

# 3) Pour les 5 plus gros, enquête sur stock.move
print(f"\n=== ENQUETE TOP 5 ===")
investigation = []
for pid, info in top20[:5]:
    p = prod_by_id[pid]
    print(f"\n--- {p.get('default_code')} {p['name'][:60]} ---")
    moves = call("stock.move", "search_read",
        [[("product_id", "=", pid), ("state", "=", "done")]],
        {"fields": ["id", "date", "name", "location_id", "location_dest_id",
                    "product_uom_qty", "quantity", "origin", "reference",
                    "sale_line_id", "purchase_line_id", "picking_id"],
         "order": "date desc", "limit": 15})
    moves_summary = []
    for mv in moves:
        src = mv["location_id"][1] if mv["location_id"] else "?"
        dst = mv["location_dest_id"][1] if mv["location_dest_id"] else "?"
        ori = mv.get("origin") or "-"
        print(f"  {mv['date'][:10]} | {mv.get('reference','-'):20} | {src[:25]:25} -> {dst[:25]:25} | qty={mv.get('quantity',0):.1f} | origin={ori}")
        moves_summary.append({
            "date": str(mv["date"])[:10],
            "ref": mv.get("reference"),
            "src": src,
            "dst": dst,
            "qty": mv.get("quantity"),
            "origin": ori,
            "sale": bool(mv.get("sale_line_id")),
            "purchase": bool(mv.get("purchase_line_id")),
        })
    investigation.append({
        "product": {"code": p.get("default_code"), "name": p["name"], "qty_neg": info["qty"]},
        "moves": moves_summary,
        "neg_locs": info["locs"],
    })

with open("C:/Users/FlowUP/Downloads/Claude/Claude/Teatower/odoo/audit_neg_invest.json", "w", encoding="utf-8") as f:
    json.dump(investigation, f, default=str, indent=2, ensure_ascii=False)

print("\nDONE")
