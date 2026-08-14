#!/usr/bin/env python3
"""
Publie les 28 boites Horeca HC250 (25 enveloppes) sur Shopify a 15,00 EUR TTC.

Mecanique retenue
-----------------
Sur teatower.com un the = UN produit Shopify avec une option "Conditionnement"
(ex. "20 infusettes" / "100 g vrac"), chaque valeur pointant vers un template Odoo
different (I0666, V0666...). Le connecteur shopify_ept gere deja ce cas.

On n'ajoute donc PAS 28 nouvelles fiches : on ajoute a chacun des 28 produits
existants une variante "25 enveloppes" (SKU HC250xxx) a 15,00 TTC. Photos, SEO,
collections et traductions du produit sont conserves.

Etapes par produit :
  1. POST /products/{id}/variants.json  (option1 = "25 enveloppes")
  2. inventory_levels/set  sur les 4 locations, depuis le stock Odoo de l'entrepot
     correspondant (Somme-Leuze<-TT, Liege<-LIEGE, Namur<-NAM, Waterloo<-WAT)
  3. creation du mapping shopify.product.product.ept pour que les commandes web
     retombent sur le bon produit Odoo

Prerequis : hc250_b2c_15eur.py --apply (list_price + liste [3] a 15,00 TTC).

Usage :  python hc250_shopify_variants.py [--apply]
"""
import os, sys, json, datetime
import xmlrpc.client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_client import shopify

APPLY = "--apply" in sys.argv

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USR = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]

OPTION_VALUE = "25 enveloppes"
PRIX_TTC = "15.00"
INSTANCE_EPT = 1

# location Shopify -> entrepot Odoo (shopify.location.ept)
LOCATIONS = {
    83611812179: 1,    # Somme-Leuze (primaire) <- TT
    84371767635: 3,    # Liege                  <- LIEGE
    84371865939: 5,    # Namur                  <- NAM
    108808798547: 4,   # Waterloo               <- WAT
}

uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USR, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def ex(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PWD, model, method, list(args), kw)


def w(m=""):
    print(m, flush=True)


w("=" * 78)
w(f"HC250 -> Shopify : variante '{OPTION_VALUE}' a {PRIX_TTC} EUR TTC"
  f"     mode={'APPLY' if APPLY else 'DRY-RUN'}")
w("=" * 78)

# --------------------------------------------------------------- 1. cote Odoo
tmpls = ex("product.template", "search_read",
           [["default_code", "like", "HC25"], ["default_code", "!=", "HC250898"]],
           fields=["id", "default_code", "name", "list_price", "barcode"],
           order="default_code")
prods = ex("product.product", "search_read", [["product_tmpl_id", "in", [t["id"] for t in tmpls]]],
           fields=["id", "default_code", "product_tmpl_id"])
prod_by_code = {p["default_code"]: p for p in prods}

# stock par entrepot (stock.quant, locations internes de chaque entrepot)
wh = ex("stock.warehouse", "read", sorted(set(LOCATIONS.values())), fields=["id", "name", "lot_stock_id"])
stock = {p["id"]: {} for p in prods}
for h in wh:
    q = ex("stock.quant", "search_read",
           [["product_id", "in", [p["id"] for p in prods]],
            ["location_id", "child_of", h["lot_stock_id"][0]]],
           fields=["product_id", "quantity"])
    for row in q:
        pid = row["product_id"][0]
        stock[pid][h["id"]] = stock[pid].get(h["id"], 0) + row["quantity"]

w(f"\n[1] {len(tmpls)} refs HC250 (HC250898 exclue), stock lu sur {len(wh)} entrepots")

# ------------------------------------------------- 2. cartographie Shopify
w("\n[2] Rattachement a la fiche Shopify du meme the (via SKU I0/V0/GI0)")
shop_prods, since = [], 0
while True:
    batch = shopify.get("products.json", params={"limit": 250, "since_id": since})["products"]
    if not batch:
        break
    shop_prods.extend(batch)
    since = batch[-1]["id"]
by_sku = {v["sku"].strip(): p for p in shop_prods for v in p["variants"] if v.get("sku")}

plan, orphelins = [], []
for t in tmpls:
    code = t["default_code"]
    suf = code[5:]
    cible = next((by_sku[k] for k in (f"I0{suf}", f"V0{suf}", f"GI0{suf}") if k in by_sku), None)
    if not cible:
        orphelins.append(code)
        continue
    deja = next((v for v in cible["variants"] if (v.get("sku") or "").strip() == code), None)
    plan.append({"code": code, "tmpl": t, "shop_product": cible, "variante_existante": deja})

w(f"    {len(plan)} rattachees, {len(orphelins)} sans fiche Shopify {orphelins}")
a_creer = [x for x in plan if not x["variante_existante"]]
w(f"    variantes a creer : {len(a_creer)} ; deja presentes : {len(plan) - len(a_creer)}")

en_stock = [x for x in a_creer if sum(stock[prod_by_code[x['code']]['id']].values()) > 0]
w(f"    dont {len(en_stock)} avec du stock -> achetables tout de suite ;"
  f" {len(a_creer) - len(en_stock)} a 0 -> affichees 'epuise' (inventory_policy=deny)")

w("\n    detail :")
for x in plan:
    pid = prod_by_code[x["code"]]["id"]
    tot = sum(stock[pid].values())
    etat = "DEJA" if x["variante_existante"] else ("creer" if tot else "creer (0 stock)")
    w(f"      {x['code']:12} -> [{x['shop_product']['id']}] {x['shop_product']['title'][:44]:46}"
      f" stock={tot:7.0f}  {etat}")

if not APPLY:
    w("\n" + "=" * 78)
    w("DRY-RUN termine - relancer avec --apply pour ecrire.")
    sys.exit(0)

# --------------------------------------------------------------- 3. ecriture
if "--limit" in sys.argv:
    n = int(sys.argv[sys.argv.index("--limit") + 1])
    a_creer = a_creer[:n]
    w(f"\n    --limit {n} : seules les {len(a_creer)} premieres refs seront traitees")

w("\n[3] Creation des variantes Shopify + stock + mapping Odoo")
resultats, echecs = [], []
for x in a_creer:
    code, t, sp = x["code"], x["tmpl"], x["shop_product"]
    pid = prod_by_code[code]["id"]
    body = {"variant": {
        "option1": OPTION_VALUE,
        "price": PRIX_TTC,
        "sku": code,
        "barcode": t["barcode"] or "",
        "inventory_management": "shopify",
        "inventory_policy": "deny",
        "taxable": True,
        "requires_shipping": True,
        "weight_unit": "kg",
    }}
    try:
        v = shopify.post(f"products/{sp['id']}/variants.json", json_body=body)["variant"]
    except Exception as e:
        echecs.append((code, f"creation variante : {e}"))
        w(f"    ECHEC {code} : {e}")
        continue

    # stock par location
    poses = []
    for loc_id, wh_id in LOCATIONS.items():
        qty = int(stock[pid].get(wh_id, 0))
        try:
            shopify.post("inventory_levels/set.json", json_body={
                "location_id": loc_id,
                "inventory_item_id": v["inventory_item_id"],
                "available": qty,
            })
            poses.append(f"{qty}")
        except Exception as e:
            poses.append("ERR")
            echecs.append((code, f"stock loc {loc_id} : {e}"))

    # mapping shopify_ept
    ept_tmpl = ex("shopify.product.template.ept", "search_read",
                  [["shopify_tmpl_id", "=", str(sp["id"])]], fields=["id"], limit=1)
    map_id = None
    if ept_tmpl:
        deja_map = ex("shopify.product.product.ept", "search",
                      [["variant_id", "=", str(v["id"])]])
        if not deja_map:
            map_id = ex("shopify.product.product.ept", "create", [{
                "name": t["name"],
                "product_id": pid,
                "shopify_template_id": ept_tmpl[0]["id"],
                "shopify_instance_id": INSTANCE_EPT,
                "variant_id": str(v["id"]),
                "default_code": code,
                "inventory_item_id": str(v["inventory_item_id"]),
                "exported_in_shopify": True,
            }])[0]
    else:
        echecs.append((code, "pas de shopify.product.template.ept pour ce produit"))

    resultats.append({"code": code, "shopify_product_id": sp["id"], "variant_id": v["id"],
                      "inventory_item_id": v["inventory_item_id"], "prix": v["price"],
                      "ept_map_id": map_id, "stock": poses})
    w(f"    OK {code:12} variante {v['id']} @ {v['price']} EUR"
      f"  stock[SL/LG/NA/WA]={'/'.join(poses)}  ept={map_id}")

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports",
                    "hc250_shopify_variants.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
json.dump({"generated": datetime.datetime.now().isoformat(),
           "resultats": resultats, "echecs": echecs}, open(path, "w"), indent=1, ensure_ascii=False)

w(f"\n{len(resultats)} variantes creees, {len(echecs)} anomalie(s)")
for c, e in echecs:
    w(f"    ! {c} : {e}")
w(f"Rapport : {path}")
