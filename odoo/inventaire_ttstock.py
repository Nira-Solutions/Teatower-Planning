#!/usr/bin/env python3
"""
Inventaire ciblé TT/Stock : ramène à 0 les quants négatifs sur les 58 produits
en déficit agrégé. Snapshot JSON avant pour réversibilité totale.

Usage :
  python odoo/inventaire_ttstock.py            # exécution réelle
  python odoo/inventaire_ttstock.py --dry-run  # préview sans écriture
"""
import sys, json, datetime as dt, pathlib, argparse
sys.stdout.reconfigure(encoding="utf-8")
import xmlrpc.client
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
SNAPSHOT_DIR = ROOT / "snapshots"
SNAPSHOT_DIR.mkdir(exist_ok=True)

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"


def connect():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PWD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    def call(model, method, args, kw=None):
        return models.execute_kw(DB, uid, PWD, model, method, args, kw or {})
    return call


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    call = connect()
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Locations TT/Stock
    locs = call("stock.location", "search",
                [[("complete_name", "ilike", "TT/Stock")]])
    print(f"Locations TT/Stock arbo : {len(locs)}")

    # 2. Tous les quants → calcul agrégé par produit
    quants = call("stock.quant", "search_read",
                  [[("location_id", "in", locs)]],
                  {"fields": ["id", "product_id", "location_id",
                              "quantity", "reserved_quantity", "inventory_quantity"]})
    agg = defaultdict(float)
    for q in quants:
        if q["product_id"]:
            agg[q["product_id"][0]] += q["quantity"]

    # 3. Produits en déficit agrégé
    deficit_pids = sorted([pid for pid, qty in agg.items() if qty < 0])
    print(f"Produits en déficit agrégé : {len(deficit_pids)}")

    # 4. Quants à nettoyer (ceux < 0 sur ces produits)
    to_clean = [q for q in quants
                if q["product_id"] and q["product_id"][0] in deficit_pids
                and q["quantity"] < 0]
    print(f"Lignes quants négatives à ramener à 0 : {len(to_clean)}")

    # 5. Snapshot complet (tous les quants des 58 produits)
    snap_quants = [q for q in quants
                   if q["product_id"] and q["product_id"][0] in deficit_pids]

    # info produits
    pinfo = call("product.product", "read", [deficit_pids],
                 {"fields": ["id", "default_code", "name", "standard_price"]})
    pmap = {p["id"]: p for p in pinfo}

    snapshot = {
        "timestamp": ts,
        "loc_ids": locs,
        "deficit_product_ids": deficit_pids,
        "products": pmap,
        "quants_before": snap_quants,
        "quants_to_clean_ids": [q["id"] for q in to_clean],
        "agg_before": {pid: agg[pid] for pid in deficit_pids},
    }
    snap_path = SNAPSHOT_DIR / f"ttstock_inventaire_{ts}.json"
    snap_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    print(f"✓ Snapshot : {snap_path}")

    # 6. Application
    if args.dry_run:
        print("DRY-RUN — aucune écriture.")
        # Aperçu top 15
        print("\nTop 15 ajustements :")
        sorted_clean = sorted(to_clean, key=lambda q: q["quantity"])[:15]
        for q in sorted_clean:
            p = pmap.get(q["product_id"][0], {})
            print(f"  {p.get('default_code') or '-':14} "
                  f"{(p.get('name') or '?')[:38]:38} "
                  f"loc#{q['location_id'][0]:5} "
                  f"qty {q['quantity']:>10,.2f} → 0")
        return

    # Application réelle : pour chaque quant, set inventory_quantity = 0 puis apply
    ok, err = 0, 0
    errors = []
    for i, q in enumerate(to_clean):
        try:
            call("stock.quant", "write",
                 [[q["id"]], {"inventory_quantity": 0.0}])
            try:
                call("stock.quant", "action_apply_inventory", [[q["id"]]])
            except xmlrpc.client.Fault as e:
                # action_apply_inventory retourne un dict non-sérialisable XML-RPC
                # mais l'opération est bien appliquée côté Odoo. On ignore cette erreur.
                if "OdooMarshaller" not in str(e) and "dumps" not in str(e):
                    raise
            # Vérification effective
            after = call("stock.quant", "read", [[q["id"]]],
                         {"fields": ["quantity"]})
            if after and abs(after[0]["quantity"]) < 0.01:
                ok += 1
            else:
                err += 1
                errors.append((q["id"], f"qty toujours {after[0]['quantity']}"))
        except Exception as e:
            err += 1
            errors.append((q["id"], str(e)[:120]))
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(to_clean)} traités…")

    print(f"\n✓ {ok}/{len(to_clean)} quants ajustés à 0")
    if err:
        print(f"⚠️ {err} erreurs :")
        for qid, msg in errors[:10]:
            print(f"  quant#{qid} : {msg}")

    # 7. Vérif après
    quants_after = call("stock.quant", "search_read",
                        [[("location_id", "in", locs),
                          ("product_id", "in", deficit_pids)]],
                        {"fields": ["product_id", "quantity"]})
    agg_after = defaultdict(float)
    for q in quants_after:
        agg_after[q["product_id"][0]] += q["quantity"]
    still_neg = [(pid, qty) for pid, qty in agg_after.items() if qty < 0]
    print(f"\nProduits encore en déficit après : {len(still_neg)}")

    # 8. Rapport markdown
    report = [f"# Inventaire TT/Stock — nettoyage déficits agrégés", "",
              f"Date : {ts}", f"Snapshot : `{snap_path.name}`", "",
              "## Résumé",
              f"- Produits ciblés : **{len(deficit_pids)}**",
              f"- Lignes quants négatives traitées : **{ok}/{len(to_clean)}**",
              f"- Produits encore en déficit après : **{len(still_neg)}**",
              "",
              "## Top 20 ajustements (avant → après agrégé)",
              "| Réf | Produit | Avant | Après | Δ |",
              "|---|---|---:|---:|---:|"]
    by_delta = sorted(deficit_pids, key=lambda pid: agg[pid])[:20]
    for pid in by_delta:
        p = pmap.get(pid, {})
        before = agg[pid]
        after = agg_after.get(pid, 0)
        delta = after - before
        report.append(f"| {p.get('default_code') or '-'} "
                      f"| {(p.get('name') or '?')[:60]} "
                      f"| {before:,.0f} | {after:,.0f} | +{delta:,.0f} |")

    if errors:
        report += ["", "## Erreurs",
                   "| Quant ID | Message |", "|---|---|"]
        for qid, msg in errors:
            report.append(f"| {qid} | {msg} |")

    report_path = ROOT / f"inventaire_ttstock_{ts}.md"
    report_path.write_text("\n".join(report), encoding="utf-8")
    print(f"✓ Rapport : {report_path}")


if __name__ == "__main__":
    main()
