"""
Accessoires A1144 + A1149-A1158 : création des fiches Shopify en BROUILLON, avec description,
SEO, photo (Odoo image_1920, ou visuel HD Dethlefsen & Balk quand Odoo n'a qu'une miniature)
+ lien connecteur Emipro (shopify.product.template.ept / product.product.ept).

Prix Shopify = list_price Odoo × 1,21 → TTC (jamais le HT).
A1145 (gobelet enfant atelier) = composante, pas vendue → exclue.
A1146-A1148 (travel cups Qwetch) existaient déjà en brouillon → exclues.

Usage : python _create_shopify_accessoires_a1144.py [A1144 …]
Garde-fou : un SKU déjà présent sur Shopify est ignoré.
"""
import base64
import json
import os
import sys
import urllib.request
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
DB_IMG = "https://www.dethlefsen-balk.de/images/IMAGE/{}.jpg"

PRODUCTS = {
    "A1144": {
        "title": "Boule à thé Carla - abeille - acier inoxydable",
        "type": "type:filtre-infuseur",
        "img_db": "41475",
        "seo_title": "Boule à thé Carla abeille en inox | Teatower",
        "seo_desc": "Boule à thé en acier inoxydable avec chaînette et sa petite abeille souriante. Idéale pour infuser votre thé en vrac à la tasse.",
        "body": """<p>La <strong>boule à thé Carla</strong> met un sourire dans chaque tasse : une boule à mailles fines en <strong>acier inoxydable</strong>, une chaînette, et au bout une <strong>petite abeille</strong> qui reste accrochée au bord de votre mug.</p>
<ul>
  <li><strong>Matière :</strong> acier inoxydable, breloque décorative abeille</li>
  <li><strong>Fermeture :</strong> clip à charnière, ouverture facile</li>
  <li><strong>Usage :</strong> infusion à la tasse de thés et infusions en vrac</li>
</ul>
<p><em>Astuce :</em> remplissez la boule à moitié seulement — les feuilles ont besoin de place pour se déployer et libérer tous leurs arômes.</p>""",
    },
    "A1149": {
        "title": "Théière Nicolo à long bec verseur - acier inoxydable noir 0,85 l",
        "type": "type:theiere-tisaniere",
        "seo_title": "Théière Nicolo long bec verseur inox 0,85 l | Teatower",
        "seo_desc": "Théière Nicolo en acier inoxydable finition noire, 0,85 l, avec long bec col de cygne pour un versement précis. Design épuré et moderne.",
        "body": """<p>La <strong>théière Nicolo</strong> se distingue par son <strong>long bec col de cygne</strong>, qui offre un versement fin et parfaitement maîtrisé. Sa ligne épurée en <strong>acier inoxydable finition noire</strong> s'invite aussi bien au service du thé qu'au comptoir.</p>
<ul>
  <li><strong>Contenance :</strong> 0,85 l</li>
  <li><strong>Matière :</strong> acier inoxydable, finition noire mate</li>
  <li><strong>Bec :</strong> long bec verseur pour un débit précis, sans goutte</li>
  <li><strong>Usage :</strong> service du thé, eau chaude pour infusion à la tasse</li>
</ul>
<p>Un objet design, robuste et facile d'entretien, à associer à une boule à thé ou un filtre pour vos thés en vrac.</p>""",
    },
    "A1150": {
        "title": "Gourde à thé nomade Alva - verre borosilicate et filtre inox 0,25 l",
        "type": "type:bouteille-mug-voyage",
        "seo_title": "Gourde à thé Alva verre et filtre inox 0,25 l | Teatower",
        "seo_desc": "Gourde à thé Alva en verre borosilicate avec filtre en acier inoxydable et bouchon bambou. 0,25 l pour emporter votre thé partout.",
        "body": """<p>La <strong>gourde Alva</strong> vous permet d'infuser votre thé en vrac et de l'emporter partout. Son <strong>filtre en acier inoxydable</strong> retient les feuilles, son <strong>verre borosilicate</strong> laisse admirer la couleur de l'infusion.</p>
<ul>
  <li><strong>Contenance :</strong> 0,25 l</li>
  <li><strong>Matière :</strong> verre borosilicate, filtre en acier inoxydable, bouchon bambou</li>
  <li><strong>Dimensions :</strong> H 21,7 cm, Ø 5,3 cm</li>
  <li><strong>Usage :</strong> thé chaud ou infusion à froid, au bureau comme en balade</li>
</ul>
<p>Format fin qui se glisse dans un sac : l'alliée des amateurs de thé nomades.</p>""",
    },
    "A1151": {
        "title": "Mug Blair en grès avec dorures 0,3 l - décor assorti",
        "type": "type:verre-tasse",
        "seo_title": "Mug Blair en grès avec dorures 0,3 l | Teatower",
        "seo_desc": "Mug Blair en grès crème, décor sapins et feuillages rehaussé de dorures, 0,3 l. Une jolie tasse d'hiver, décor assorti.",
        "body": """<p>Le <strong>mug Blair</strong> habille vos pauses thé d'un décor d'hiver tout en douceur : <strong>grès crème</strong>, motifs de sapins et de feuillages, <strong>touches dorées</strong> et anse noire contrastée.</p>
<ul>
  <li><strong>Contenance :</strong> 0,3 l</li>
  <li><strong>Matière :</strong> grès avec dorures</li>
  <li><strong>Dimensions :</strong> H 9 cm, Ø 7 cm</li>
  <li><strong>Décor :</strong> 2 décors assortis, livré selon disponibilité</li>
</ul>
<p><em>Entretien :</em> dorures — lavage à la main recommandé, ne pas passer au micro-ondes.</p>""",
    },
    "A1152": {
        "title": "Mug Melchior rouge - pain d'épices - grès soft-touch 0,55 l",
        "type": "type:verre-tasse",
        "seo_title": "Mug de Noël Melchior rouge 0,55 l | Teatower",
        "seo_desc": "Grand mug de Noël Melchior rouge, décor bonshommes pain d'épices et sucres d'orge, grès toucher velours 0,55 l, intérieur moucheté.",
        "body": """<p>Le <strong>mug Melchior rouge</strong> sent bon les fêtes : <strong>bonshommes pain d'épices</strong>, sucres d'orge et flocons sur un grès au <strong>toucher velouté soft-touch</strong>, avec un intérieur moucheté assorti.</p>
<ul>
  <li><strong>Contenance :</strong> 0,55 l — un grand mug pour les longues infusions d'hiver</li>
  <li><strong>Matière :</strong> grès, finition soft-touch, décor intérieur</li>
  <li><strong>Coloris :</strong> rouge (existe aussi en vert)</li>
</ul>
<p>Parfait avec un rooibos de Noël ou un thé noir épicé — et une idée cadeau toute trouvée.</p>""",
    },
    "A1153": {
        "title": "Boule à thé Christmas Cat - chat sucre d'orge - inox Ø 5 cm",
        "type": "type:filtre-infuseur",
        "seo_title": "Boule à thé de Noël chat sucre d'orge Ø 5 cm | Teatower",
        "seo_desc": "Boule à thé de Noël en inox 18/8, Ø 5 cm, avec sa breloque petit chat au bonnet de Père Noël et sucre d'orge. Idée cadeau.",
        "body": """<p>Une <strong>boule à thé de Noël</strong> irrésistible : sa breloque représente un <strong>petit chat coiffé d'un bonnet de Père Noël</strong>, serrant son sucre d'orge. Il reste suspendu au bord de la tasse pendant que votre thé infuse.</p>
<ul>
  <li><strong>Matière :</strong> acier inoxydable 18/8, breloque décorative</li>
  <li><strong>Diamètre :</strong> Ø 5 cm</li>
  <li><strong>Usage :</strong> infusion à la tasse de thés et infusions en vrac</li>
</ul>
<p>Petit prix, grand effet : le cadeau idéal à glisser sous le sapin ou dans un calendrier. Existe aussi en version renne.</p>""",
    },
    "A1154": {
        "title": "Mug Winter Forest - grès à émail réactif 0,45 l - décor assorti",
        "type": "type:verre-tasse",
        "seo_title": "Mug Winter Forest grès émail réactif 0,45 l | Teatower",
        "seo_desc": "Mug Winter Forest en grès noir à émail réactif, décor forêt d'hiver, 0,45 l. Chaque pièce est unique. Décor assorti.",
        "body": """<p>Le <strong>mug Winter Forest</strong> évoque une forêt de sapins sous un ciel d'hiver. Son <strong>émail réactif</strong> coule en nuances violines sur le grès noir : <strong>chaque pièce est unique</strong>.</p>
<ul>
  <li><strong>Contenance :</strong> 0,45 l</li>
  <li><strong>Matière :</strong> grès, émail réactif</li>
  <li><strong>Décor :</strong> 2 décors assortis, livré selon disponibilité</li>
</ul>
<p>Une tasse généreuse et chaleureuse pour les soirées d'hiver, à offrir avec un thé de saison.</p>""",
    },
    "A1155": {
        "title": "Boîte à thé Christmas Ornaments 125 g - métal mat",
        "type": "type:boite-the",
        "seo_title": "Boîte à thé de Noël Christmas Ornaments 125 g | Teatower",
        "seo_desc": "Boîte à thé ronde en métal mat, décor boules de Noël et maisonnette, couvercle coiffant, 125 g. Conserve votre thé à l'abri de la lumière.",
        "body": """<p>La <strong>boîte à thé Christmas Ornaments</strong> conserve votre thé en vrac avec un décor de fête : boules de Noël, petite maison en pain d'épices et sapins sur un <strong>métal finition mate</strong> vert d'eau.</p>
<ul>
  <li><strong>Contenance :</strong> environ 125 g de thé</li>
  <li><strong>Matière :</strong> métal, finition mate</li>
  <li><strong>Fermeture :</strong> couvercle coiffant</li>
  <li><strong>Dimensions :</strong> H 13 cm, Ø 8,6 cm</li>
</ul>
<p>Une boîte métal opaque protège le thé de la lumière, de l'humidité et des odeurs. Remplie de votre thé préféré, c'est un cadeau prêt à offrir.</p>""",
    },
    "A1156": {
        "title": "Mug Christmas Ornaments - New Bone China mat en relief 0,35 l",
        "type": "type:verre-tasse",
        "seo_title": "Mug de Noël Christmas Ornaments 0,35 l | Teatower",
        "seo_desc": "Mug de Noël Christmas Ornaments en New Bone China mat avec décor en relief, 0,35 l. Assorti à la boîte à thé de la collection.",
        "body": """<p>Le <strong>mug Christmas Ornaments</strong> reprend le décor de fête de la collection : boules de Noël, petite voiture rouge et sapins, sur une porcelaine <strong>New Bone China</strong> au fini mat et au <strong>décor en relief</strong>.</p>
<ul>
  <li><strong>Contenance :</strong> 0,35 l</li>
  <li><strong>Matière :</strong> New Bone China, finition mate, relief</li>
  <li><strong>Collection :</strong> assorti à la boîte à thé Christmas Ornaments</li>
</ul>
<p>Associez-le à la boîte assortie et à un thé de Noël pour composer un cadeau complet.</p>""",
    },
    "A1157": {
        "title": "Mug Melchior vert - pain d'épices - grès soft-touch 0,55 l",
        "type": "type:verre-tasse",
        "seo_title": "Mug de Noël Melchior vert 0,55 l | Teatower",
        "seo_desc": "Grand mug de Noël Melchior vert, décor bonshommes pain d'épices et sucres d'orge, grès toucher velours 0,55 l, intérieur moucheté.",
        "body": """<p>Le <strong>mug Melchior vert</strong> sent bon les fêtes : <strong>bonshommes pain d'épices</strong>, sucres d'orge et flocons sur un grès au <strong>toucher velouté soft-touch</strong>, avec un intérieur moucheté assorti.</p>
<ul>
  <li><strong>Contenance :</strong> 0,55 l — un grand mug pour les longues infusions d'hiver</li>
  <li><strong>Matière :</strong> grès, finition soft-touch, décor intérieur</li>
  <li><strong>Coloris :</strong> vert (existe aussi en rouge)</li>
</ul>
<p>Parfait avec un rooibos de Noël ou un thé noir épicé — et une idée cadeau toute trouvée.</p>""",
    },
    "A1158": {
        "title": "Boule à thé Christmas Cat - chat renne - inox Ø 5 cm",
        "type": "type:filtre-infuseur",
        "seo_title": "Boule à thé de Noël chat renne Ø 5 cm | Teatower",
        "seo_desc": "Boule à thé de Noël en inox 18/8, Ø 5 cm, avec sa breloque petit chat aux bois de renne et écharpe. Idée cadeau.",
        "body": """<p>Une <strong>boule à thé de Noël</strong> pleine de tendresse : sa breloque représente un <strong>petit chat déguisé en renne</strong>, bois sur la tête et écharpe au cou. Il reste suspendu au bord de la tasse pendant que votre thé infuse.</p>
<ul>
  <li><strong>Matière :</strong> acier inoxydable 18/8, breloque décorative</li>
  <li><strong>Diamètre :</strong> Ø 5 cm</li>
  <li><strong>Usage :</strong> infusion à la tasse de thés et infusions en vrac</li>
</ul>
<p>Petit prix, grand effet : le cadeau idéal à glisser sous le sapin. Existe aussi en version sucre d'orge.</p>""",
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
                 fields=["id", "name", "list_price", "standard_price", "taxes_id", "barcode", "weight",
                         "categ_id", "image_1920"])[0]
        variant_id = x("product.product", "search", [["product_tmpl_id", "=", tmpl["id"]]])[0]
        rate = x("account.tax", "read", tmpl["taxes_id"], ["amount"])[0]["amount"] / 100.0
        price_ttc = round(tmpl["list_price"] * (1 + rate), 2)
        marge = (tmpl["list_price"] - tmpl["standard_price"]) / tmpl["list_price"]
        print(f"[{sku}] « {tmpl['name']} » TTC {price_ttc:.2f} (marge {marge:.1%})")

        found = shopify.graphql('query($q:String!){productVariants(first:1,query:$q){nodes{sku product{id title status}}}}',
                                {"q": f'sku:"{sku}"'})["productVariants"]["nodes"]
        if [n for n in found if n["sku"] == sku]:
            print(f"[{sku}] EXISTE DÉJÀ sur Shopify : {found[0]['product']} — ignoré")
            continue
        if x("shopify.product.template.ept", "search_count", [["product_tmpl_id", "=", tmpl["id"]]]):
            print(f"[{sku}] lien Emipro déjà présent — ignoré")
            continue

        sp = shopify.post("products.json", json_body={"product": {
            "title": spec["title"], "body_html": spec["body"], "vendor": "Teatower",
            "product_type": "Accessoire thé", "status": "draft",
            "tags": ["accessoires", spec["type"]],
            "metafields_global_title_tag": spec["seo_title"],
            "metafields_global_description_tag": spec["seo_desc"],
            "variants": [{"sku": sku, "price": f"{price_ttc:.2f}", "barcode": tmpl.get("barcode") or "",
                          "weight": tmpl.get("weight") or 0, "weight_unit": "kg",
                          "inventory_management": "shopify", "inventory_policy": "deny",
                          "requires_shipping": True, "taxable": True}],
        }})["product"]
        v = sp["variants"][0]
        print(f"[{sku}] Shopify créé {sp['id']} (status {sp['status']}) handle={sp['handle']}")

        if spec.get("img_db"):
            raw = urllib.request.urlopen(DB_IMG.format(spec["img_db"]), timeout=30).read()
            img_b64, fname = base64.b64encode(raw).decode(), f"{sp['handle']}.jpg"
        else:
            img_b64, fname = tmpl["image_1920"], f"{sp['handle']}.jpg"
        img = shopify.post(f"products/{sp['id']}/images.json", json_body={"image": {
            "attachment": img_b64, "filename": fname, "alt": spec["title"]}})["image"]
        print(f"[{sku}] photo {img['width']}x{img['height']}")

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


if __name__ == "__main__":
    main(sys.argv[1:] or list(PRODUCTS))
