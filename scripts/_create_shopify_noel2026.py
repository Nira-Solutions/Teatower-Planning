"""
Coffrets Noël 2026 (C0195-C0198) : création des fiches Shopify en BROUILLON (pas encore de photos)
+ lien connecteur Emipro (shopify.product.template.ept / product.product.ept).

Prix Shopify = list_price Odoo × (1 + TVA) → TTC.
Collections : « Coffrets et cadeaux » est une collection AUTOMATIQUE sur le titre
(coffret / cadeau / calendrier…) → le titre doit contenir l'un de ces mots. TVA 6 % = manuelle.

Usage : python _create_shopify_noel2026.py C0195 [C0196 …]
Garde-fou : un SKU déjà présent sur Shopify est ignoré.
"""
import json
import os
import sys
import xmlrpc.client
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shopify_client import shopify

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
MAPPING_FILE = ROOT / "output" / "shopify_odoo_mapping.json"

ODOO_URL = "https://tea-tree.odoo.com"
ODOO_DB = "tsc-be-tea-tree-main-18515272"
ODOO_USER = "nicolas.raes@teatower.com"
ODOO_PWD = os.environ["ODOO_PWD"]
INSTANCE_ID = 1
COLLECTION_TVA6 = "gid://shopify/Collection/625483186515"

PRODUCTS = {
    "C0195": {
        "title": "Calendrier de l'Avent 2026 - 24 moments magiques, thés et infusions - Teatower",
        "seo_title": "Calendrier de l'Avent 2026 thés et infusions | Teatower",
        "seo_desc": ("Calendrier de l'Avent Teatower 2026 : 24 cases, 24 recettes de thés noirs, verts, "
                     "rooibos, maté et infusions, dont les créations de Noël. Une infusette par jour jusqu'au 24 décembre."),
        "body": """<p><strong>24 cases, 24 recettes, 24 moments rien qu'à vous.</strong> Du 1er au 24 décembre, chaque matin s'ouvre sur une nouvelle tasse : des thés noirs, verts, un pu erh, des rooibos, un maté et des infusions — nos grands classiques et les recettes de Noël de l'année.</p>

<p>Chaque case renferme une infusette emballée individuellement. Le menu du calendrier présente chaque recette avec sa famille, ses arômes et ses conseils de préparation.</p>

<h3>Les 24 recettes du calendrier</h3>
<p><strong>Thés noirs</strong></p>
<ul>
  <li><strong>Blue Earl Grey BIO</strong> — bergamote et bleuet</li>
  <li><strong>Matin enneigé</strong> — amande, pomme et cannelle</li>
  <li><strong>Spéculoos &amp; Cie</strong> — cardamome, amande et cannelle</li>
  <li><strong>Caramel beurre salé</strong> — thé noir parfumé au caramel</li>
  <li><strong>Délice de Montélimar</strong> — amande, miel et nougat</li>
</ul>
<p><strong>Thés verts</strong></p>
<ul>
  <li><strong>Orangipane</strong> — amande, orange et fleur d'oranger</li>
  <li><strong>Marrakech Sunset BIO</strong> — menthe et fleur d'oranger</li>
  <li><strong>Le thé des amoureux</strong> — fraise, rose et lavande</li>
</ul>
<p><strong>Pu erh, rooibos et maté</strong></p>
<ul>
  <li><strong>Hansel &amp; Gretel</strong> — pu erh, cannelle, badiane, cacao et amande</li>
  <li><strong>Gourmandise de Noël</strong> — rooibos à l'amande</li>
  <li><strong>Jardin de Babylone</strong> — rooibos cassis, fraise et sureau</li>
  <li><strong>Pêche de vigne BIO</strong> — rooibos à la pêche</li>
  <li><strong>Silhouette</strong> — maté, menthe poivrée, citronnelle et orange</li>
</ul>
<p><strong>Infusions de fruits</strong></p>
<ul>
  <li><strong>Trésor des lutins</strong> — chocolat et noisette</li>
  <li><strong>Récolte enchantée</strong> — orange et cannelle</li>
  <li><strong>Au coin du feu</strong> — pomme, cerise et cannelle</li>
  <li><strong>La nana de Wépion</strong> — fraise, ananas, cerise et papaye</li>
  <li><strong>Le panier de grand maman</strong> — fraise, mûre, cassis et framboise</li>
  <li><strong>Pomme vanille</strong> — pomme, citron et vanille</li>
</ul>
<p><strong>Infusions de plantes et d'épices</strong></p>
<ul>
  <li><strong>Plaisir chocolaté</strong> — chocolat et amande</li>
  <li><strong>Masala Chai</strong> — mélange d'épices</li>
  <li><strong>Ginger Hot</strong> — gingembre et citronnelle</li>
  <li><strong>Sérénité BIO</strong> — menthe, rose et lavande</li>
  <li><strong>Namasté BIO</strong> — verveine, orange et citron</li>
</ul>

<h3>Préparation</h3>
<ul>
  <li>Thés noirs et pu erh : eau à 90-95 °C, 3 à 5 minutes.</li>
  <li>Thés verts : eau à 75 °C, 2 à 3 minutes.</li>
  <li>Rooibos : eau à 90-100 °C, 5 à 8 minutes.</li>
  <li>Maté et infusions : eau frémissante, 5 à 10 minutes.</li>
</ul>

<p><em>Le compagnon de décembre à offrir — ou à s'offrir — pour attendre Noël une tasse à la main.</em></p>""",
    },
}


def main(codes):
    uid = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common").authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)

    def x(model, method, *args, **kw):
        return models.execute_kw(ODOO_DB, uid, ODOO_PWD, model, method, list(args), kw)

    mapping = json.loads(MAPPING_FILE.read_text(encoding="utf-8")) if MAPPING_FILE.exists() else {}

    for sku in codes:
        spec = PRODUCTS[sku]
        tmpl = x("product.template", "search_read", [["default_code", "=", sku]],
                 fields=["id", "name", "list_price", "taxes_id", "barcode", "weight", "categ_id"])[0]
        variant_id = x("product.product", "search", [["product_tmpl_id", "=", tmpl["id"]]])[0]
        rate = x("account.tax", "read", tmpl["taxes_id"], ["amount"])[0]["amount"] / 100.0
        price_ttc = round(tmpl["list_price"] * (1 + rate), 2)
        print(f"[{sku}] Odoo « {tmpl['name']} » HT {tmpl['list_price']:.4f} -> TTC {price_ttc:.2f}")

        found = shopify.graphql('query($q:String!){productVariants(first:1,query:$q){nodes{product{id title status}}}}',
                                {"q": f'sku:"{sku}"'})["productVariants"]["nodes"]
        if found:
            print(f"[{sku}] EXISTE DÉJÀ sur Shopify : {found[0]['product']} — ignoré")
            continue

        sp = shopify.post("products.json", json_body={"product": {
            "title": spec["title"], "body_html": spec["body"], "vendor": "Teatower",
            "product_type": "Coffret cadeau", "status": "draft",
            "tags": ["Coffret", "Noël 2026", "odoo-sync", f"sku:{sku}"],
            "metafields_global_title_tag": spec["seo_title"],
            "metafields_global_description_tag": spec["seo_desc"],
            "variants": [{"sku": sku, "price": f"{price_ttc:.2f}", "barcode": tmpl.get("barcode") or "",
                          "weight": tmpl.get("weight") or 0, "weight_unit": "kg",
                          "inventory_management": "shopify", "inventory_policy": "deny",
                          "requires_shipping": True, "taxable": True}],
        }})["product"]
        v = sp["variants"][0]
        print(f"[{sku}] Shopify créé {sp['id']} (status {sp['status']}) handle={sp['handle']}")

        if rate == 0.06:
            err = shopify.graphql("mutation($id:ID!,$p:[ID!]!){collectionAddProducts(id:$id,productIds:$p){userErrors{message}}}",
                                  {"id": COLLECTION_TVA6, "p": [sp["admin_graphql_api_id"]]})
            print(f"[{sku}] collection TVA 6 % : {err['collectionAddProducts']['userErrors'] or 'OK'}")

        t_ept = x("shopify.product.template.ept", "create", {
            "name": spec["title"], "product_tmpl_id": tmpl["id"], "shopify_instance_id": INSTANCE_ID,
            "shopify_tmpl_id": str(sp["id"]), "exported_in_shopify": True,
            "website_published": "unpublished", "shopify_product_category": tmpl["categ_id"][0]})
        x("shopify.product.product.ept", "create", {
            "name": spec["title"], "default_code": sku, "product_id": variant_id, "shopify_template_id": t_ept,
            "shopify_instance_id": INSTANCE_ID, "variant_id": str(v["id"]),
            "inventory_item_id": str(v["inventory_item_id"]), "exported_in_shopify": True,
            "inventory_management": "shopify", "check_product_stock": "deny", "taxable": True})
        print(f"[{sku}] lien connecteur Emipro créé (template ept {t_ept})")

        mapping[sku] = {"odoo_template_id": tmpl["id"], "odoo_name": tmpl["name"], "shopify_product_id": sp["id"],
                        "shopify_handle": sp["handle"], "shopify_variant_id": v["id"], "created_status": sp["status"]}
        MAPPING_FILE.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")
        store = os.environ.get("SHOPIFY_STORE", "").split(".")[0]
        print(f"[{sku}] admin : https://admin.shopify.com/store/{store}/products/{sp['id']}")


if __name__ == "__main__":
    main(sys.argv[1:] or list(PRODUCTS))
