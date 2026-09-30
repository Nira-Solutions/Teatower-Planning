"""
Accessoires Dethlefsen & Balk Noël 2026 : scission des articles « 2 assortis » en 1 réf par coloris.

  A1152 Mug Melchior (2 assortis)          -> A1152 rouge  + A1157 vert   (D&B 32567)
  A1153 Boule Christmas Cats (2 assortis)  -> A1153 canne à sucre + A1158 renne (D&B 41292)

La 1re réf est renommée, la 2de est une copie du template (prix, taxes, catégorie, fournisseur).
Photo : visuel D&B (.de/images/IMAGE/<art>.jpg) coupé en deux — gauche = 1re réf, droite = 2de.
Aucune PO / SO / stock sur A1152-A1153 au 30/09/2026 : renommage sans impact.
Idempotent.
"""
import base64
import io
import os
import sys
import urllib.request
import xmlrpc.client

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

ODOO_URL = "https://tea-tree.odoo.com"
ODOO_DB = "tsc-be-tea-tree-main-18515272"
ODOO_USER = "nicolas.raes@teatower.com"
ODOO_PWD = os.environ["ODOO_PWD"]
SPLIT_AT = {"41292": 0.525}   # la chaîne du chat de gauche dépasse le milieu
LANGS_ORDER = ["en_US", "nl_NL", "fr_FR", "fr_BE"]   # français en dernier

SPLITS = [
    {
        "src": "A1152", "new": "A1157", "art": "32567",
        "left": {
            "name": {"en_US": "Melchior mug red - soft-touch stoneware with inner decor 0.55 L",
                     "nl_NL": "Mok Melchior rood - steengoed soft-touch met binnendecor 0,55 L",
                     "fr_FR": "Mug Melchior rouge - grès toucher velours, décor intérieur 0,55 L",
                     "fr_BE": "Mug Melchior rouge - grès toucher velours, décor intérieur 0,55 L"},
            "desc": {"en_US": "Soft-touch stoneware with inner decor, red, 0.55 l.",
                     "nl_NL": "Steengoed met soft-touch en binnendecor, rood, 0,55 l.",
                     "fr_FR": "Grès avec toucher velours et décor intérieur, coloris rouge, 0,55 l.",
                     "fr_BE": "Grès avec toucher velours et décor intérieur, coloris rouge, 0,55 l."},
            "supplier_name": "Melchior Becher - rot",
        },
        "right": {
            "name": {"en_US": "Melchior mug green - soft-touch stoneware with inner decor 0.55 L",
                     "nl_NL": "Mok Melchior groen - steengoed soft-touch met binnendecor 0,55 L",
                     "fr_FR": "Mug Melchior vert - grès toucher velours, décor intérieur 0,55 L",
                     "fr_BE": "Mug Melchior vert - grès toucher velours, décor intérieur 0,55 L"},
            "desc": {"en_US": "Soft-touch stoneware with inner decor, green, 0.55 l.",
                     "nl_NL": "Steengoed met soft-touch en binnendecor, groen, 0,55 l.",
                     "fr_FR": "Grès avec toucher velours et décor intérieur, coloris vert, 0,55 l.",
                     "fr_BE": "Grès avec toucher velours et décor intérieur, coloris vert, 0,55 l."},
            "supplier_name": "Melchior Becher - grün",
        },
    },
    {
        "src": "A1153", "new": "A1158", "art": "41292",
        "left": {
            "name": {"en_US": "Christmas Cat tea ball candy cane - 18/8 stainless steel Ø 5 cm",
                     "nl_NL": "Theebal Christmas Cat zuurstok - RVS 18/8 Ø 5 cm",
                     "fr_FR": "Boule à thé Christmas Cat canne à sucre - inox 18/8 Ø 5 cm",
                     "fr_BE": "Boule à thé Christmas Cat canne à sucre - inox 18/8 Ø 5 cm"},
            "desc": {"en_US": "18/8 stainless steel, cat charm with Santa hat and candy cane, Ø 5 cm.",
                     "nl_NL": "RVS 18/8, kattenhanger met kerstmuts en zuurstok, Ø 5 cm.",
                     "fr_FR": "Acier inoxydable 18/8, breloque chat au bonnet de Noël et canne à sucre, Ø 5 cm.",
                     "fr_BE": "Acier inoxydable 18/8, breloque chat au bonnet de Noël et canne à sucre, Ø 5 cm."},
            "supplier_name": "Christmas Cats Teesieb - Zuckerstange",
        },
        "right": {
            "name": {"en_US": "Christmas Cat tea ball reindeer - 18/8 stainless steel Ø 5 cm",
                     "nl_NL": "Theebal Christmas Cat rendier - RVS 18/8 Ø 5 cm",
                     "fr_FR": "Boule à thé Christmas Cat renne - inox 18/8 Ø 5 cm",
                     "fr_BE": "Boule à thé Christmas Cat renne - inox 18/8 Ø 5 cm"},
            "desc": {"en_US": "18/8 stainless steel, cat charm with reindeer antlers, Ø 5 cm.",
                     "nl_NL": "RVS 18/8, kattenhanger met rendiergewei, Ø 5 cm.",
                     "fr_FR": "Acier inoxydable 18/8, breloque chat aux bois de renne, Ø 5 cm.",
                     "fr_BE": "Acier inoxydable 18/8, breloque chat aux bois de renne, Ø 5 cm."},
            "supplier_name": "Christmas Cats Teesieb - Rentier",
        },
    },
]


def half_image(art, side):
    """Moitié gauche/droite du visuel D&B, recentrée sur fond blanc au format d'origine (4:3)."""
    with urllib.request.urlopen(f"https://www.dethlefsen-balk.de/images/IMAGE/{art}.jpg", timeout=30) as r:
        img = Image.open(io.BytesIO(r.read())).convert("RGB")
    w, h = img.size
    cut = int(w * SPLIT_AT.get(art, 0.5))
    half = img.crop((0, 0, cut, h) if side == "left" else (cut, 0, w, h))
    # rognage au sujet (pixels non blancs) + marge
    gray = half.convert("L").point(lambda v: 255 if v < 240 else 0)
    box = gray.getbbox()
    subj = half.crop(box)
    side_px = int(max(subj.size) * 1.25)
    canvas = Image.new("RGB", (side_px, side_px), "white")
    canvas.paste(subj, ((side_px - subj.width) // 2, (side_px - subj.height) // 2))
    buf = io.BytesIO()
    canvas.save(buf, "JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode()


def set_cost(x, code, cost):
    """copy() ne reprend pas standard_price."""
    p = x("product.product", "search_read", [["default_code", "=", code]], fields=["id"])[0]
    x("product.product", "write", [p["id"]], {"standard_price": cost})


def main():
    uid = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common").authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)

    def x(model, method, *args, **kw):
        return models.execute_kw(ODOO_DB, uid, ODOO_PWD, model, method, list(args), kw)

    def tmpl_of(code):
        t = x("product.template", "search_read",
              [["default_code", "=", code], ["active", "in", [True, False]]], fields=["id", "seller_ids"])
        return t[0] if t else None

    for s in SPLITS:
        src = tmpl_of(s["src"])
        if not src:
            raise SystemExit(f"{s['src']} introuvable")
        new = tmpl_of(s["new"])
        if not new:
            new_id = x("product.template", "copy", src["id"], {"default_code": s["new"]})
            new = tmpl_of(s["new"]) or {"id": new_id, "seller_ids": []}
            print(f"{s['new']}: template #{new['id']} créé (copie de {s['src']})")
        else:
            print(f"{s['new']}: template #{new['id']} existant")

        src_seller = x("product.supplierinfo", "read", src["seller_ids"][:1],
                       fields=["partner_id", "product_code", "price", "min_qty", "delay", "currency_id"])[0]

        for tid, variant, side in [(src["id"], s["left"], "left"), (new["id"], s["right"], "right")]:
            for lang in LANGS_ORDER:
                x("product.template", "write", [tid],
                  {"name": variant["name"][lang], "description_sale": variant["desc"][lang]},
                  context={"lang": lang})
            x("product.template", "write", [tid], {"image_1920": half_image(s["art"], side)})
            sellers = x("product.template", "read", [tid], fields=["seller_ids"])[0]["seller_ids"]
            sv = {"product_name": variant["supplier_name"]}
            if sellers:
                x("product.supplierinfo", "write", sellers[:1], sv)
            else:
                x("product.supplierinfo", "create", {
                    **sv, "product_tmpl_id": tid,
                    "partner_id": src_seller["partner_id"][0], "product_code": src_seller["product_code"],
                    "price": src_seller["price"], "min_qty": src_seller["min_qty"],
                    "delay": src_seller["delay"], "currency_id": src_seller["currency_id"][0],
                })

        set_cost(x, s["new"], src_seller["price"])

        # relecture
        for code in (s["src"], s["new"]):
            t = tmpl_of(code)
            r = x("product.template", "read", [t["id"]],
                  fields=["list_price", "standard_price", "taxes_id", "categ_id", "available_in_pos",
                          "sale_ok", "purchase_ok", "is_storable", "seller_ids"])[0]
            sel = x("product.supplierinfo", "read", r["seller_ids"],
                    fields=["partner_id", "product_code", "product_name", "price", "min_qty"])
            print(f"  {code}: PV HT {r['list_price']:.2f} (TTC {r['list_price'] * 1.21:.2f}) | coût {r['standard_price']} "
                  f"| taxes {r['taxes_id']} | {r['categ_id'][1]} | PoS {r['available_in_pos']} | stockable {r['is_storable']}")
            for sl in sel:
                print(f"     fournisseur {sl['partner_id'][1]} art. {sl['product_code']} « {sl['product_name']} » {sl['price']} € min {sl['min_qty']}")
            for lang in ["fr_BE", "fr_FR", "en_US", "nl_NL"]:
                n = x("product.template", "read", [t["id"]], fields=["name"], context={"lang": lang})[0]["name"]
                print(f"     {lang}: {n}")


if __name__ == "__main__":
    main()
