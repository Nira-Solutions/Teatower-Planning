"""Audit cible TT/Stock + descendantes : pourquoi ces locations sont negatives."""
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

# 1) Identifier TT/Stock et toutes descendantes (parent_path / child_of)
tt_root = call("stock.location", "search_read",
    [[("complete_name", "=", "TT/Stock")]],
    {"fields": ["id", "complete_name", "warehouse_id", "parent_path", "usage"]})
print(f"TT/Stock root candidates: {tt_root}")
if not tt_root:
    # fallback par nom
    tt_root = call("stock.location", "search_read",
        [[("name", "=", "Stock"), ("warehouse_id.code", "=", "TT")]],
        {"fields": ["id", "complete_name", "parent_path", "warehouse_id"]})
    print(f"fallback: {tt_root}")

tt_root_id = tt_root[0]["id"]

# Enfants : child_of
tt_locs = call("stock.location", "search_read",
    [[("id", "child_of", tt_root_id), ("usage", "=", "internal")]],
    {"fields": ["id", "complete_name", "parent_path"]})
tt_loc_ids = [l["id"] for l in tt_locs]
loc_by_id = {l["id"]: l for l in tt_locs}
print(f"Locations sous TT/Stock: {len(tt_loc_ids)}")

# 2) Quants negatifs sur ces locations
neg = call("stock.quant", "search_read",
    [[("location_id", "in", tt_loc_ids), ("quantity", "<", 0)]],
    {"fields": ["id", "product_id", "location_id", "quantity",
                "reserved_quantity", "in_date"]})
print(f"Quants negatifs sous TT/Stock: {len(neg)}")

prod_ids = list({q["product_id"][0] for q in neg})
prods = call("product.product", "read", [prod_ids],
    {"fields": ["id", "default_code", "name", "standard_price",
                "qty_available", "virtual_available", "type",
                "route_ids", "bom_ids"]})
prod_by_id = {p["id"]: p for p in prods}

# Total
total_qty = sum(q["quantity"] for q in neg)
total_val = sum(q["quantity"] * prod_by_id[q["product_id"][0]].get("standard_price", 0) for q in neg)
print(f"Total qty neg TT/Stock+desc: {total_qty:.1f}  /  valeur: {total_val:.2f} EUR")

# Repartition par sous-location
by_loc = defaultdict(lambda: {"qty": 0, "n": 0})
for q in neg:
    lid = q["location_id"][0]
    by_loc[lid]["qty"] += q["quantity"]
    by_loc[lid]["n"] += 1

print("\n=== REPARTITION PAR SOUS-LOCATION TT/Stock ===")
loc_repartition = []
for lid, info in sorted(by_loc.items(), key=lambda x: x[1]["qty"]):
    lname = loc_by_id[lid]["complete_name"]
    print(f"{lname:55} | n={info['n']:4} | qty={info['qty']:.1f}")
    loc_repartition.append({"loc": lname, "n": info["n"], "qty": info["qty"]})

# Top 15 quants par |qty|
neg_sorted = sorted(neg, key=lambda q: q["quantity"])
print("\n=== TOP 15 QUANTS NEGATIFS (TT/Stock+desc) ===")
top15_quants = []
for q in neg_sorted[:15]:
    p = prod_by_id[q["product_id"][0]]
    lname = q["location_id"][1]
    val = q["quantity"] * p.get("standard_price", 0)
    print(f"[{p.get('default_code') or '-':6}] {p['name'][:38]:38} | {lname[:38]:38} | qty={q['quantity']:8.1f} | val={val:8.2f}")
    top15_quants.append({
        "code": p.get("default_code"),
        "name": p["name"],
        "loc": lname,
        "qty": q["quantity"],
        "val": val,
        "reserved": q.get("reserved_quantity"),
        "in_date": str(q.get("in_date") or ""),
    })

# 3) Top 5 produits (somme par produit) -> 10 derniers stock.move chrono
by_prod = defaultdict(lambda: {"qty": 0, "locs": []})
for q in neg:
    pid = q["product_id"][0]
    by_prod[pid]["qty"] += q["quantity"]
    by_prod[pid]["locs"].append((q["location_id"][1], q["quantity"]))

top5 = sorted(by_prod.items(), key=lambda x: x[1]["qty"])[:5]

print("\n=== ENQUETE TOP 5 PRODUITS sur TT/Stock+desc ===")
investigations = []
for pid, info in top5:
    p = prod_by_id[pid]
    print(f"\n--- {p.get('default_code')} {p['name'][:55]} | total neg={info['qty']:.1f} ---")
    # Moves done OU sortants depuis TT/Stock+desc OU entrants vers TT/Stock+desc
    moves = call("stock.move", "search_read",
        [[("product_id", "=", pid), ("state", "=", "done"),
          "|", ("location_id", "in", tt_loc_ids), ("location_dest_id", "in", tt_loc_ids)]],
        {"fields": ["id", "date", "name", "location_id", "location_dest_id",
                    "product_uom_qty", "quantity", "origin", "reference",
                    "sale_line_id", "purchase_line_id", "picking_id",
                    "production_id", "raw_material_production_id"],
         "order": "date asc", "limit": 50})
    # garde les 20 derniers chronologiques (ordre asc) pour voir le passage sous zero
    moves_show = moves[-20:] if len(moves) > 20 else moves

    inv_moves = []
    cum = 0
    for mv in moves_show:
        src = mv["location_id"][1] if mv["location_id"] else "?"
        dst = mv["location_dest_id"][1] if mv["location_dest_id"] else "?"
        is_in = mv["location_dest_id"][0] in tt_loc_ids if mv.get("location_dest_id") else False
        is_out = mv["location_id"][0] in tt_loc_ids if mv.get("location_id") else False
        # net flow sur TT/Stock+desc
        delta = 0
        if is_in and not is_out:
            delta = mv.get("quantity", 0)
        elif is_out and not is_in:
            delta = -mv.get("quantity", 0)
        cum += delta
        kind = "MO" if mv.get("production_id") else (
               "MOraw" if mv.get("raw_material_production_id") else (
               "PO" if mv.get("purchase_line_id") else (
               "SO" if mv.get("sale_line_id") else "INT")))
        ori = mv.get("origin") or "-"
        ref = mv.get("reference") or "-"
        flag = " <-- NEG" if cum < 0 else ""
        print(f"  {mv['date'][:10]} | {kind:5} | {ref[:18]:18} | {src[:28]:28} -> {dst[:28]:28} | qty={mv.get('quantity',0):7.1f} | delta={delta:7.1f} | cum={cum:7.1f}{flag}")
        inv_moves.append({
            "date": str(mv["date"])[:10],
            "kind": kind,
            "ref": ref,
            "src": src,
            "dst": dst,
            "qty": mv.get("quantity"),
            "delta": delta,
            "cum_after": cum,
            "origin": ori,
        })
    investigations.append({
        "code": p.get("default_code"),
        "name": p["name"],
        "qty_neg_total": info["qty"],
        "neg_locs": info["locs"],
        "moves": inv_moves,
    })

# 4) Comptage patterns sur TOUS les moves recents qui touchent TT/Stock+desc
print("\n=== PATTERNS GLOBAUX (90 derniers jours) ===")
import datetime
since = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
recent_out = call("stock.move", "search_read",
    [[("state", "=", "done"), ("date", ">=", since),
      ("location_id", "in", tt_loc_ids)]],
    {"fields": ["id", "location_id", "location_dest_id",
                "production_id", "raw_material_production_id",
                "purchase_line_id", "sale_line_id", "quantity"],
     "limit": 5000})
print(f"Moves sortants TT/Stock+desc 90j: {len(recent_out)}")

cnt = {"MO_consume": 0, "SO_out": 0, "internal_to_mag": 0,
       "internal_intra_tt": 0, "other_out": 0}
qty = {k: 0 for k in cnt}
for mv in recent_out:
    dst_id = mv["location_dest_id"][0] if mv.get("location_dest_id") else 0
    dst_name = mv["location_dest_id"][1] if mv.get("location_dest_id") else ""
    q = mv.get("quantity", 0)
    if mv.get("raw_material_production_id"):
        cnt["MO_consume"] += 1; qty["MO_consume"] += q
    elif mv.get("sale_line_id"):
        cnt["SO_out"] += 1; qty["SO_out"] += q
    elif dst_id in tt_loc_ids:
        cnt["internal_intra_tt"] += 1; qty["internal_intra_tt"] += q
    elif "Stock" in dst_name and dst_name.split("/")[0] != "TT":
        cnt["internal_to_mag"] += 1; qty["internal_to_mag"] += q
    else:
        cnt["other_out"] += 1; qty["other_out"] += q

for k in cnt:
    print(f"  {k:22} | n={cnt[k]:5} | qty={qty[k]:.0f}")

# 5) Sauve
out = {
    "tt_root_id": tt_root_id,
    "n_locs_tt": len(tt_loc_ids),
    "n_quants_neg": len(neg),
    "total_qty_neg": total_qty,
    "total_value_neg": total_val,
    "by_subloc": loc_repartition,
    "top15_quants": top15_quants,
    "top5_invest": investigations,
    "patterns_90d": {"counts": cnt, "qty": qty,
                     "total_moves_out": len(recent_out)},
}
with open("C:/Users/FlowUP/Downloads/Claude/Claude/Teatower/odoo/audit_tt_stock.json", "w", encoding="utf-8") as f:
    json.dump(out, f, default=str, indent=2, ensure_ascii=False)

print("\nDONE")
