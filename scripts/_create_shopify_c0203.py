"""
C0203 — Coffret en bois 8 références (32 enveloppes) : photos détourées -> Odoo + Shopify.

 1. image_1920 du product.template Odoo = photo principale détourée.
 2. Création du produit Shopify (ACTIF, prix TTC, 3 photos, collections coffrets).
 3. Lien connecteur Emipro (shopify.product.template.ept / product.product.ept)
    pour que le stock Odoo et les commandes se synchronisent.
Photos : output/photos_C0203/ (générées par le détourage rembg birefnet).
"""
import base64
import json
import os
import sys
import xmlrpc.client
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shopify_client import shopify

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "output" / "photos_C0203"
MAPPING_FILE = ROOT / "output" / "shopify_odoo_mapping.json"

ODOO_URL = "https://tea-tree.odoo.com"
ODOO_DB = "tsc-be-tea-tree-main-18515272"
ODOO_USER = "nicolas.raes@teatower.com"
ODOO_PWD = os.environ["ODOO_PWD"]

SKU = "C0203"
INSTANCE_ID = 1
COLLECTIONS = [
    "gid://shopify/Collection/617636102483",  # Coffrets et cadeaux thés et infusions
    "gid://shopify/Collection/625483186515",  # TVA 6%
    "gid://shopify/Collection/693574893907",  # Catalogue eligible promo
]
IMAGES = [  # ordre d'affichage Shopify
    ("C0203_ouvert_face.jpg", "Coffret en bois Teatower ouvert, 8 compartiments garnis de thés et infusions en enveloppes"),
    ("C0203_ouvert_dessus.jpg", "Coffret en bois Teatower vu de dessus avec les 8 références de thés et infusions"),
    ("C0203_ferme.jpg", "Couvercle du coffret en bois Teatower gravé du logo Taste the World"),
]

TITLE = "Coffret en bois garni - 8 thés et infusions, 32 enveloppes - Teatower"
BODY = """<p><strong>Le coffret en bois qui fait voyager d'une tasse à l'autre.</strong> Huit compartiments, huit recettes : des thés noirs, verts, un rooibos et des infusions, pour que chacun trouve son thé — et en découvre un qu'il n'attendait pas.</p>

<p>Un bel objet en bois foncé, couvercle gravé du logo Teatower, intérieur bleu nuit. Une fois les enveloppes dégustées, il se garde comme boîte à thé et se remplit à nouveau.</p>

<h3>Ce que contient le coffret</h3>
<p>4 enveloppes de chacune des 8 références, soit <strong>32 enveloppes</strong> emballées individuellement :</p>
<ul>
  <li><strong>Blue Earl Grey BIO</strong> — thé noir, bergamote et bleuet</li>
  <li><strong>English Breakfast</strong> — thé noir tannique et puissant</li>
  <li><strong>Sencha BIO</strong> — thé vert végétal et doux</li>
  <li><strong>Vert Jasmin</strong> — thé vert au jasmin</li>
  <li><strong>Oasis du désert BIO</strong> — thé vert à la menthe</li>
  <li><strong>Pêche de vigne BIO</strong> — rooibos à la pêche, sans théine</li>
  <li><strong>Le panier de grand maman</strong> — infusion fraise et mûre</li>
  <li><strong>Lady Dodo</strong> — infusion tilleul et fenouil, idéale le soir</li>
</ul>

<h3>Préparation</h3>
<ul>
  <li>Thés noirs : eau à 95 °C, 3 à 4 minutes.</li>
  <li>Thés verts : eau à 75-80 °C, 2 à 3 minutes.</li>
  <li>Rooibos et infusions : eau frémissante, 5 à 7 minutes.</li>
</ul>

<p><em>Un cadeau prêt à offrir — fêtes de fin d'année, remerciements, cadeau d'affaires ou simple envie de se faire plaisir.</em></p>"""
SEO_TITLE = "Coffret en bois garni 8 thés et infusions | Teatower"
SEO_DESC = ("Coffret cadeau en bois Teatower : 8 compartiments, 32 enveloppes de thés noirs, "
            "verts, rooibos et infusions, dont 4 BIO. Un cadeau prêt à offrir, une boîte à garder.")


def main():
    uid = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common").authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)

    def x(model, method, *args, **kw):
        return models.execute_kw(ODOO_DB, uid, ODOO_PWD, model, method, list(args), kw)

    tmpl = x("product.template", "search_read", [["default_code", "=", SKU]],
             fields=["id", "name", "list_price", "taxes_id", "barcode", "weight", "categ_id"])[0]
    variant_id = x("product.product", "search", [["product_tmpl_id", "=", tmpl["id"]]])[0]
    rate = x("account.tax", "read", tmpl["taxes_id"], ["amount"])[0]["amount"] / 100.0
    price_ttc = round(tmpl["list_price"] * (1 + rate), 2)
    print(f"[odoo] {tmpl['name']} HT={tmpl['list_price']:.4f} -> TTC={price_ttc}")

    # 1. Photo principale sur la fiche Odoo
    main_b64 = base64.b64encode((PHOTOS / IMAGES[0][0]).read_bytes()).decode()
    x("product.template", "write", [tmpl["id"]], {"image_1920": main_b64})
    print("[odoo] image_1920 posée")

    # 2. Shopify — garde-fou doublon
    res = shopify.post("graphql.json", json_body={
        "query": 'query($q:String!){productVariants(first:1,query:$q){edges{node{product{id title}}}}}',
        "variables": {"q": f'sku:"{SKU}"'}})
    if res["data"]["productVariants"]["edges"]:
        print("[shopify] EXISTE DÉJÀ :", res["data"]["productVariants"]["edges"][0]["node"]); return 1

    payload = {"product": {
        "title": TITLE, "body_html": BODY, "vendor": "Teatower", "product_type": "Coffret cadeau",
        "status": "active", "tags": ["Coffret", "odoo-sync", f"sku:{SKU}"],
        "metafields_global_title_tag": SEO_TITLE, "metafields_global_description_tag": SEO_DESC,
        "variants": [{"sku": SKU, "price": f"{price_ttc:.2f}", "barcode": tmpl.get("barcode") or "",
                      "weight": tmpl.get("weight") or 0, "weight_unit": "kg",
                      "inventory_management": "shopify", "inventory_policy": "deny",
                      "requires_shipping": True, "taxable": True}],
        "images": [{"attachment": base64.b64encode((PHOTOS / f).read_bytes()).decode(), "alt": alt}
                   for f, alt in IMAGES],
    }}
    sp = shopify.post("products.json", json_body=payload)["product"]
    v = sp["variants"][0]
    print(f"[shopify] créé {sp['id']} handle={sp['handle']} images={len(sp['images'])}")

    for cid in COLLECTIONS:
        shopify.post("graphql.json", json_body={
            "query": "mutation($id:ID!,$p:[ID!]!){collectionAddProducts(id:$id,productIds:$p){userErrors{message}}}",
            "variables": {"id": cid, "p": [sp["admin_graphql_api_id"]]}})
    print("[shopify] collections ajoutées")

    # 3. Lien connecteur Emipro
    t_ept = x("shopify.product.template.ept", "create", {
        "name": TITLE, "product_tmpl_id": tmpl["id"], "shopify_instance_id": INSTANCE_ID,
        "shopify_tmpl_id": str(sp["id"]), "exported_in_shopify": True,
        "website_published": "published_global", "shopify_product_category": tmpl["categ_id"][0]})
    x("shopify.product.product.ept", "create", {
        "name": TITLE, "default_code": SKU, "product_id": variant_id, "shopify_template_id": t_ept,
        "shopify_instance_id": INSTANCE_ID, "variant_id": str(v["id"]),
        "inventory_item_id": str(v["inventory_item_id"]), "exported_in_shopify": True,
        "inventory_management": "shopify", "check_product_stock": "deny", "taxable": True})
    print(f"[odoo] lien connecteur créé (template ept {t_ept})")

    mapping = json.loads(MAPPING_FILE.read_text(encoding="utf-8")) if MAPPING_FILE.exists() else {}
    mapping[SKU] = {"odoo_template_id": tmpl["id"], "odoo_name": tmpl["name"], "shopify_product_id": sp["id"],
                    "shopify_handle": sp["handle"], "shopify_variant_id": v["id"], "created_status": sp["status"]}
    MAPPING_FILE.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"URL : https://teatower.com/products/{sp['handle']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
