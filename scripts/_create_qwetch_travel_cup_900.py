"""
Pré-commande Qwetch 15/09/2026 : 3 travel cups 900 ml avec bouchon étanche.

 1. Crée les produits Odoo (A1146-A1148) sur le modèle de A1104 : accessoire 21 %,
    stockable, route Buy, dispo en caisse, fournisseur Qwetch — nom écrit dans les 4 langues.
 2. Crée les règles de réassort des 4 magasins (LIEGE / NAM / WAT / ROC).
 3. Ajoute 32 pièces de chaque sur le bon de commande P00621.
 4. Crée les fiches Shopify en BROUILLON (le connecteur shopify_ept les mappe par SKU).

Idempotent : chaque étape vérifie l'existant. Sans --apply : simulation.
Mot de passe Odoo lu dans ODOO_PWD (dépôt public, jamais en clair).
"""
import os
import sys
import xmlrpc.client
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

APPLY = "--apply" in sys.argv
URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]

QWETCH = 6417
PO_NAME = "P00621"
PO_QTY = 32
LANGS = ["fr_BE", "fr_FR", "en_US", "nl_NL"]

PRODUCTS = [
    # ref Teatower, SKU Qwetch, EAN, collection, coloris
    ("A1146", "QD6117E", "3700735907502", "Flowers", "Bleu nuit"),
    ("A1147", "QD6116E", "3700735907496", "Flowers", "Pastel rose"),
    ("A1148", "QD6113E", "3700735907380", "Cozy", "Lin"),
]
PRICE_TTC = 45.0      # tarif public Qwetch
PRICE_PA = 22.5       # tarif revendeur HT 01/02/2026

# (warehouse_id, location_id, route_id, min, max) — 14 pièces en magasin sur 32
STORE_ORDERPOINTS = [
    (3, 4524, 43, 2, 4),   # Liège
    (5, 4540, 44, 2, 4),   # Namur
    (4, 4532, 29, 2, 4),   # Waterloo
    (9, 4712, 53, 1, 2),   # Rocourt
]

uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def x(model, method, args, kw=None):
    return models.execute_kw(DB, uid, PWD, model, method, args, kw or {})


def odoo_product(ref, sku, ean, collection, color):
    name = f"Travel cup isotherme avec bouchon étanche - {collection} - {color} - 900ml Qwetch"
    found = x("product.template", "search_read",
              [["|", ["default_code", "=", ref], ["barcode", "=", ean]]],
              {"fields": ["id", "default_code"], "context": {"active_test": False}})
    if found:
        tid = found[0]["id"]
        print(f"[odoo] {ref} existe déjà (template {tid})")
    elif not APPLY:
        print(f"[odoo] SIMULATION création {ref} {name}")
        return None, name
    else:
        tid = x("product.template", "create", [{
            "name": name,
            "default_code": ref,
            "barcode": ean,
            "type": "consu",
            "is_storable": True,
            "categ_id": 66,
            "pos_categ_ids": [(6, 0, [60])],
            "available_in_pos": True,
            "sale_ok": True,
            "purchase_ok": True,
            "list_price": round(PRICE_TTC / 1.21, 4),
            "standard_price": PRICE_PA,
            "taxes_id": [(6, 0, [3])],
            "supplier_taxes_id": [(6, 0, [16])],
            "route_ids": [(6, 0, [5])],
            "invoice_policy": "order",
            "purchase_method": "receive",
            "responsible_id": 6,
            "seller_ids": [(0, 0, {"partner_id": QWETCH, "product_code": sku,
                                   "price": PRICE_PA, "min_qty": 1, "delay": 3})],
        }])
        print(f"[odoo] {ref} créé (template {tid})")
    if APPLY:
        for lang in LANGS:
            x("product.template", "write", [[tid], {"name": name}], {"context": {"lang": lang}})
    pid = x("product.product", "search", [[["product_tmpl_id", "=", tid]]])[0]

    for wh, loc, route, mn, mx in STORE_ORDERPOINTS:
        if x("stock.warehouse.orderpoint", "search", [[["product_id", "=", pid], ["warehouse_id", "=", wh]]]):
            continue
        if APPLY:
            x("stock.warehouse.orderpoint", "create", [{
                "product_id": pid, "warehouse_id": wh, "location_id": loc, "route_id": route,
                "product_min_qty": mn, "product_max_qty": mx, "trigger": "auto"}])
        print(f"[odoo] {ref} orderpoint entrepôt {wh} {mn}/{mx}")
    return pid, name


def add_po_lines(pids):
    po = x("purchase.order", "search_read", [[["name", "=", PO_NAME]]], {"fields": ["id", "state", "partner_id"]})[0]
    assert po["partner_id"][0] == QWETCH, po
    existing = {l["product_id"][0] for l in x("purchase.order.line", "search_read",
                [[["order_id", "=", po["id"]]]], {"fields": ["product_id"]})}
    for pid in pids:
        if pid in existing:
            print(f"[po] produit {pid} déjà sur {PO_NAME}")
            continue
        if APPLY:
            x("purchase.order.line", "create", [{"order_id": po["id"], "product_id": pid,
                                                  "product_qty": PO_QTY, "price_unit": PRICE_PA}])
        print(f"[po] {PO_NAME} + {PO_QTY} x produit {pid}")


def shopify_draft(ref, ean, name, collection, color):
    from shopify_client import shopify
    q = {"query": 'query($q:String!){productVariants(first:1,query:$q){edges{node{product{id status}}}}}',
         "variables": {"q": f'sku:"{ref}"'}}
    edges = shopify.post("graphql.json", json_body=q)["data"]["productVariants"]["edges"]
    if edges:
        print(f"[shopify] {ref} existe déjà : {edges[0]['node']['product']}")
        return
    body = (
        f"<p>La <strong>travel cup isotherme 900 ml Qwetch</strong> de la collection "
        f"<strong>{collection}</strong>, coloris {color.lower()}, emporte vos thés glacés et "
        f"infusions froides partout. En <strong>acier inoxydable</strong> isotherme, avec "
        f"<strong>bouchon étanche</strong> pour la glisser dans un sac sans crainte.</p>"
    )
    payload = {"product": {
        "title": name,
        "body_html": body,
        "vendor": "Teatower",
        "product_type": "Accessoire thé",
        "tags": "accessoires, type:bouteille-mug-voyage",
        "status": "draft",
        "metafields_global_title_tag": f"Travel cup isotherme {collection} {color.lower()} 900ml Qwetch",
        "metafields_global_description_tag": (
            f"Travel cup isotherme Qwetch 900 ml, collection {collection} {color.lower()}, "
            f"inox et bouchon étanche. Idéale pour vos thés glacés."),
        "variants": [{"sku": ref, "price": f"{PRICE_TTC:.2f}", "barcode": ean,
                      "inventory_management": "shopify", "taxable": True}],
    }}
    if not APPLY:
        print(f"[shopify] SIMULATION brouillon {ref}")
        return
    sp = shopify.post("products.json", json_body=payload)["product"]
    print(f"[shopify] {ref} brouillon créé id={sp['id']} status={sp['status']}")


if __name__ == "__main__":
    pids = []
    for ref, sku, ean, collection, color in PRODUCTS:
        pid, name = odoo_product(ref, sku, ean, collection, color)
        if pid:
            pids.append(pid)
        shopify_draft(ref, ean, name, collection, color)
    if pids:
        add_po_lines(pids)
