"""
C0195 — Calendrier de l'Avent 2026 : photo -> Shopify + Odoo, activation de la fiche.

La fiche Shopify a été créée en brouillon par _create_shopify_noel2026.py (sans photo).
 1. Ajout de la photo boîte fermée (output/photos_C0195/C0195_ferme.jpg) sur Shopify.
 2. image_1920 du product.template Odoo = même photo.
 3. Fiche Shopify -> active + publiée sur la boutique en ligne.
La photo boîte ouverte n'est PAS publiée : le logo généré y lit « RELMON TEA HOUSE ».
"""
import base64, json, os, sys, xmlrpc.client
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shopify_client import shopify

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "output" / "photos_C0195" / "C0195_ferme.jpg"
MAPPING = json.loads((ROOT / "output" / "shopify_odoo_mapping.json").read_text(encoding="utf-8"))["C0195"]
PID, TMPL = MAPPING["shopify_product_id"], MAPPING["odoo_template_id"]
ALT = "Calendrier de l'Avent 2026 Teatower, 24 moments magiques de thés et infusions, boîte fermée"

b64 = base64.b64encode(PHOTO.read_bytes()).decode()
p = shopify.get(f"products/{PID}.json")["product"]
if not p["images"]:
    img = shopify.post(f"products/{PID}/images.json", {"image": {"attachment": b64, "alt": ALT, "position": 1}})["image"]
    print(f"[shopify] image {img['id']} ajoutée")
p = shopify.put(f"products/{PID}.json", {"product": {"id": PID, "status": "active", "published": True}})["product"]
print(f"[shopify] status={p['status']} published_at={p['published_at']} images={len(p['images'])} handle={p['handle']}")

U = "https://tea-tree.odoo.com"; D = "tsc-be-tea-tree-main-18515272"
uid = xmlrpc.client.ServerProxy(U + "/xmlrpc/2/common").authenticate(D, "nicolas.raes@teatower.com", os.environ["ODOO_PWD"], {})
xmlrpc.client.ServerProxy(U + "/xmlrpc/2/object").execute_kw(D, uid, os.environ["ODOO_PWD"], "product.template", "write", [[TMPL], {"image_1920": b64}])
print(f"[odoo] image_1920 posée sur product.template {TMPL}")
