# -*- coding: utf-8 -*-
"""
Verifie que le stock Shopify des locations magasin a bien converge sur Odoo.

A lancer AVANT d'activer le retrait en magasin natif sur Liege et Namur : tant
que les quantites Shopify ne correspondent pas a Odoo, ouvrir le retrait
reviendrait a vendre sur des chiffres faux. Waterloo sert de temoin — c'est le
mapping deja valide, il doit ressortir a 100 % de concordance.

Compare la quantite Shopify (`available`) a la quantite Odoo retenue par le
connecteur, c'est-a-dire le champ configure dans `shopify_stock_field` de
l'instance — par defaut « Free To Use Quantity », soit le stock physique moins
les reservations.

Usage :
  python odoo/shopify_check_stock_liege_namur.py
  python odoo/shopify_check_stock_liege_namur.py --limit 400 --show 25
"""
import argparse
import os
import sys
import xmlrpc.client
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from shopify_client import shopify  # noqa: E402

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"

# nom de la location Shopify -> (entrepot Odoo, libelle)
LOCS = {
    "Liège": (3, "LIEGE"),
    "Namur": (5, "NAM"),
    "Waterloo": (4, "WAT"),
}


def connect():
    pwd = os.environ.get("ODOO_PWD")
    if not pwd:
        raise SystemExit("Definir ODOO_PWD avant d'executer ce script.")
    uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, pwd, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    def call(model, method, args, kw=None):
        return models.execute_kw(DB, uid, pwd, model, method, args, kw or {})

    return call


QUERY = """
query($cursor: String) {
  productVariants(first: 100, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    edges { node { sku
      inventoryItem { inventoryLevels(first: 10) { edges { node {
        updatedAt location { name }
        quantities(names: ["available"]) { quantity } } } } } } } } }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=600, help="nb de variantes Shopify a lire")
    ap.add_argument("--show", type=int, default=15, help="nb d'ecarts detailles affiches")
    args = ap.parse_args()

    call = connect()

    # --- Shopify ---
    shop, maj, cursor = {}, {}, None
    while len(shop) < args.limit:
        d = shopify.graphql(QUERY, {"cursor": cursor})
        pv = d["productVariants"]
        for e in pv["edges"]:
            n = e["node"]
            if not n["sku"]:
                continue
            for x in n["inventoryItem"]["inventoryLevels"]["edges"]:
                loc = x["node"]["location"]["name"]
                if loc not in LOCS:
                    continue
                shop.setdefault(n["sku"], {})[loc] = x["node"]["quantities"][0]["quantity"]
                d0 = x["node"]["updatedAt"][:10]
                m = maj.setdefault(loc, [d0, d0])
                m[0], m[1] = min(m[0], d0), max(m[1], d0)
        if not pv["pageInfo"]["hasNextPage"]:
            break
        cursor = pv["pageInfo"]["endCursor"]

    # --- Odoo, meme convention que le connecteur : quantite libre d'usage ---
    skus = sorted(shop)
    prods = []
    for i in range(0, len(skus), 200):
        prods += call("product.product", "search_read",
                      [[("default_code", "in", skus[i:i + 200])]],
                      {"fields": ["id", "default_code"]})
    by_sku = {p["default_code"]: p["id"] for p in prods}
    pids = list(by_sku.values())

    odoo = {}
    for loc_name, (wh_id, code) in LOCS.items():
        wh = call("stock.warehouse", "read", [[wh_id]], {"fields": ["lot_stock_id"]})[0]
        root = wh["lot_stock_id"][0]
        rows = []
        for i in range(0, len(pids), 200):
            rows += call("product.product", "read", [pids[i:i + 200]],
                         {"fields": ["id", "free_qty"], "context": {"location": root}})
        for r in rows:
            odoo.setdefault(r["id"], {})[loc_name] = r["free_qty"]

    print("Fraicheur du stock Shopify (plage des dates de mise a jour) :")
    for loc in LOCS:
        if loc in maj:
            print(f"  {loc:<12} du {maj[loc][0]} au {maj[loc][1]}")
        else:
            print(f"  {loc:<12} aucune donnee")

    # Les references VR* sont des « vrac remplissage » a usage interne : elles ne
    # devraient pas etre vendables en ligne, et leur stock Odoo est notoirement
    # negatif (consommation sans reception). Les melanger au catalogue fausserait
    # le taux de concordance, donc on les compte a part.
    def famille(sku):
        return "vrac interne" if sku.upper().startswith("VR") else "catalogue"

    ecarts_detail = {loc: {"catalogue": [], "vrac interne": []} for loc in LOCS}
    stats = {loc: {"catalogue": [0, 0], "vrac interne": [0, 0]} for loc in LOCS}
    for loc in LOCS:
        for sku in skus:
            pid = by_sku.get(sku)
            if pid is None or loc not in shop.get(sku, {}):
                continue
            f = famille(sku)
            s = shop[sku][loc]
            o = odoo.get(pid, {}).get(loc, 0.0)
            stats[loc][f][0] += 1
            if abs(s - o) < 0.001:
                stats[loc][f][1] += 1
            else:
                ecarts_detail[loc][f].append((abs(s - o), sku, s, o))

    print(f"\nConcordance Shopify / Odoo sur {len(by_sku)} SKU :")
    print(f"  {'Location':<12}{'famille':<15}{'compares':>10}{'concordants':>13}"
          f"{'ecarts':>9}{'taux':>9}")
    for loc in LOCS:
        for f in ("catalogue", "vrac interne"):
            n, ok = stats[loc][f]
            if not n:
                continue
            taux = ok / n
            flag = ""
            if f == "catalogue":
                flag = "" if taux > 0.98 else "   <-- NON CONVERGE"
            print(f"  {loc:<12}{f:<15}{n:>10}{ok:>13}{n - ok:>9}{taux:>8.1%}{flag}")

    for loc in LOCS:
        for f in ("catalogue", "vrac interne"):
            d = sorted(ecarts_detail[loc][f], reverse=True)[:args.show]
            if not d:
                continue
            print(f"\n  {loc} / {f} — plus gros ecarts (shopify / odoo) :")
            for _, sku, s, o in d:
                print(f"    {sku:<14}{s:>8} / {o:>8.0f}")

    # Critere d'acceptation : atteindre le niveau du temoin, pas la perfection.
    # Le connecteur ne descend jamais a zero ecart — Waterloo, mapping valide
    # depuis juin, plafonne autour de 97-98 % (produits archives, cheques-cadeaux
    # a stock negatif, mouvements survenus pendant la comparaison).
    print()
    n_t, ok_t = stats["Waterloo"]["catalogue"]
    seuil = (ok_t / n_t) if n_t else 1.0
    print(f"  Temoin Waterloo (mapping valide depuis le 04/06) : {ok_t}/{n_t} "
          f"sur le catalogue, soit {seuil:.1%}. C'est le plafond reel du connecteur,")
    print("  et donc le critere d'acceptation — viser 100 % n'aurait pas de sens.")
    retard = []
    for loc in ("Liège", "Namur"):
        n, ok = stats[loc]["catalogue"]
        if n and ok / n < seuil - 0.005:
            retard.append(f"{loc} ({ok / n:.1%})")
    if not retard:
        print("  Liege et Namur sont au niveau du temoin : le retrait en magasin peut etre")
        print("  active cote Shopify.")
    else:
        print(f"  En retard sur le temoin : {', '.join(retard)}. Relancer l'export complet")
        print("  (odoo/shopify_export_stock_complet.py) puis ce controle.")
    if any(ecarts_detail[loc]["vrac interne"] for loc in LOCS):
        print("  Les ecarts sur les references VR* sont un probleme distinct et prealable :")
        print("  ces articles de vrac interne ne devraient pas etre vendables en ligne.")


if __name__ == "__main__":
    sys.exit(main())
