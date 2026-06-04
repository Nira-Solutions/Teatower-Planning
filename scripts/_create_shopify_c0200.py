"""
Create Odoo product C0200 in Shopify as DRAFT and persist the Odoo <-> Shopify link.

Steps:
 1. Pull C0200 from Odoo (template + variant + image + descriptions).
 2. Check Shopify by SKU (GraphQL productVariants query) — abort if already there.
 3. Create Shopify product (status=draft) with title, body_html, vendor, image, variant SKU+price.
 4. Persist mapping in output/shopify_odoo_mapping.json.
 5. Log internal note on Odoo product.template with shopify_product_id.
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
MAPPING_FILE = ROOT / "output" / "shopify_odoo_mapping.json"
MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)

ODOO_URL = "https://tea-tree.odoo.com"
ODOO_DB = "tsc-be-tea-tree-main-18515272"
ODOO_USER = "nicolas.raes@teatower.com"
ODOO_PWD = os.environ.get("ODOO_API_KEY") or os.environ.get("ODOO_PASSWORD") or "Teatower123"

SKU = "C0200"


def odoo_connect():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    if not uid:
        raise RuntimeError("Odoo auth failed")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return uid, models


def odoo_search_read(models, uid, model, domain, fields, limit=None):
    return models.execute_kw(
        ODOO_DB, uid, ODOO_PWD,
        model, "search_read",
        [domain, fields],
        {"limit": limit} if limit else {},
    )


def main():
    uid, models = odoo_connect()
    print(f"[odoo] connected uid={uid}")

    templates = odoo_search_read(
        models, uid, "product.template",
        [("default_code", "=", SKU)],
        ["id", "name", "default_code", "list_price", "barcode",
         "description_sale", "description", "categ_id", "image_1920",
         "weight", "type", "taxes_id"],
    )
    if not templates:
        prods = odoo_search_read(
            models, uid, "product.product",
            [("default_code", "=", SKU)],
            ["id", "product_tmpl_id"],
        )
        if not prods:
            print(f"[odoo] NOT FOUND: {SKU}")
            return 1
        tmpl_id = prods[0]["product_tmpl_id"][0]
        templates = odoo_search_read(
            models, uid, "product.template",
            [("id", "=", tmpl_id)],
            ["id", "name", "default_code", "list_price", "barcode",
             "description_sale", "description", "categ_id", "image_1920",
             "weight", "type", "taxes_id"],
        )
    tmpl = templates[0]
    # Shopify Teatower est configuré taxes_included=True : le prix poussé doit être TTC.
    # list_price Odoo est HT -> appliquer la TVA vente du produit (6% thé, 21% accessoires).
    tax_rate = 0.0
    if tmpl.get("taxes_id"):
        taxes = odoo_search_read(
            models, uid, "account.tax",
            [("id", "in", tmpl["taxes_id"])],
            ["amount", "price_include"],
        )
        if taxes and not taxes[0].get("price_include"):
            tax_rate = taxes[0]["amount"] / 100.0
    price_ttc = round(tmpl["list_price"] * (1 + tax_rate), 2)
    print(f"[odoo] found tmpl id={tmpl['id']} name={tmpl['name']!r} price HT={tmpl['list_price']} -> TTC={price_ttc}")

    sku_to_use = tmpl["default_code"] or SKU
    variant_query = f'sku:"{sku_to_use}"'
    gql = {
        "query": """
        query($q: String!) {
          productVariants(first: 5, query: $q) {
            edges { node { id sku product { id title status } } }
          }
        }
        """,
        "variables": {"q": variant_query},
    }
    res = shopify.post("graphql.json", json_body=gql)
    edges = (res.get("data") or {}).get("productVariants", {}).get("edges", [])
    if edges:
        node = edges[0]["node"]
        print(f"[shopify] ALREADY EXISTS: variant {node['sku']} on product {node['product']['title']!r} ({node['product']['id']}) status={node['product']['status']}")
        return 0

    body_html = tmpl.get("description_sale") or tmpl.get("description") or ""
    if body_html and not body_html.lstrip().startswith("<"):
        body_html = "<p>" + body_html.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"

    payload = {
        "product": {
            "title": tmpl["name"],
            "body_html": body_html,
            "vendor": "Teatower",
            "status": "draft",
            "tags": ["odoo-sync", f"sku:{sku_to_use}"],
            "variants": [{
                "sku": sku_to_use,
                "price": f"{price_ttc:.2f}",
                "barcode": tmpl.get("barcode") or "",
                "weight": tmpl.get("weight") or 0,
                "weight_unit": "kg",
                "inventory_management": "shopify",
                "requires_shipping": tmpl.get("type") != "service",
            }],
        }
    }
    if tmpl.get("image_1920"):
        payload["product"]["images"] = [{
            "attachment": tmpl["image_1920"],
            "alt": tmpl["name"],
        }]

    created = shopify.post("products.json", json_body=payload)
    sp = created["product"]
    print(f"[shopify] CREATED draft product id={sp['id']} handle={sp['handle']}")
    print(f"          admin URL: https://admin.shopify.com/store/{os.environ['SHOPIFY_STORE'].split('.')[0]}/products/{sp['id']}")

    mapping = {}
    if MAPPING_FILE.exists():
        mapping = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    mapping[sku_to_use] = {
        "odoo_template_id": tmpl["id"],
        "odoo_name": tmpl["name"],
        "shopify_product_id": sp["id"],
        "shopify_handle": sp["handle"],
        "shopify_variant_id": sp["variants"][0]["id"] if sp.get("variants") else None,
        "created_status": sp["status"],
    }
    MAPPING_FILE.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[mapping] saved to {MAPPING_FILE}")

    note = (
        f"<p><b>Synchronisation Shopify</b><br>"
        f"Produit cree en <b>brouillon</b> sur Shopify.<br>"
        f"Shopify product ID : <code>{sp['id']}</code><br>"
        f"Handle : <code>{sp['handle']}</code><br>"
        f"Admin URL : <a href=\"https://admin.shopify.com/store/{os.environ['SHOPIFY_STORE'].split('.')[0]}/products/{sp['id']}\">ouvrir</a></p>"
    )
    models.execute_kw(
        ODOO_DB, uid, ODOO_PWD,
        "product.template", "message_post",
        [[tmpl["id"]]],
        {"body": note, "message_type": "comment", "subtype_xmlid": "mail.mt_note"},
    )
    print(f"[odoo] internal note logged on product.template {tmpl['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
