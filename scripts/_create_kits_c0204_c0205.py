"""
Kits bundle -10 % (nomenclature KIT / phantom) — Odoo uniquement.

  C0204  Kit Matcha      : V0895 + A0297 + A1133     52,00 TTC séparément -> 45,90 TTC (TVA 21 %, kit mixte)
  C0205  Kit Noël 2026   : V0711 + V0732 + V0891 + V0917 + V0918
                                                      60,00 TTC séparément -> 53,90 TTC (TVA 6 %)

Modèle : C0202 (consu non stockable, vendable, PoS, pas achetable, BoM phantom).
Idempotent : relancer ne recrée ni produit ni BoM.
"""
import os
import sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8")

ODOO_URL = "https://tea-tree.odoo.com"
ODOO_DB = "tsc-be-tea-tree-main-18515272"
ODOO_USER = "nicolas.raes@teatower.com"
ODOO_PWD = os.environ["ODOO_PWD"]

TAX_21, TAX_6 = 3, 8
CATEG_COFFRET = 65                 # All / Coffret
POS_COFFRET, POS_NOEL = 27, 47     # Coffret / NOEL 2025

KITS = [
    {
        "code": "C0204",
        "ttc": 45.90,
        "tax": TAX_21,
        "pos": [POS_COFFRET],
        "names": {
            "en_US": "Matcha Kit - Japanese matcha 50 g, bamboo whisk and Shado Chawan bowl",
            "nl_NL": "Matchaset - Japanse matcha 50 g, bamboe klopper en Shado Chawan-kom",
            "fr_FR": "Kit Matcha - Matcha japonais 50 g, fouet bambou et bol Chawan Shado",
            "fr_BE": "Kit Matcha - Matcha japonais 50 g, fouet bambou et bol Chawan Shado",
        },
        "lines": [("V0895", 1), ("A0297", 1), ("A1133", 1)],
    },
    {
        "code": "C0205",
        "ttc": 53.90,
        "tax": TAX_6,
        "pos": [POS_COFFRET, POS_NOEL],
        "names": {
            "en_US": "Christmas Kit 2026 - the 5 Christmas teas and infusions (5 x 100 g)",
            "nl_NL": "Kerstset 2026 - de 5 kersttheeën en -infusies (5 x 100 g)",
            "fr_FR": "Kit Noël 2026 - les 5 thés et infusions de Noël (5 x 100 g)",
            "fr_BE": "Kit Noël 2026 - les 5 thés et infusions de Noël (5 x 100 g)",
        },
        "lines": [("V0711", 1), ("V0732", 1), ("V0891", 1), ("V0917", 1), ("V0918", 1)],
    },
]
TAX_RATE = {TAX_21: 0.21, TAX_6: 0.06}
LANGS_ORDER = ["en_US", "nl_NL", "fr_FR", "fr_BE"]   # français en dernier


def main():
    uid = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common").authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)

    def x(model, method, *args, **kw):
        return models.execute_kw(ODOO_DB, uid, ODOO_PWD, model, method, list(args), kw)

    for kit in KITS:
        code = kit["code"]
        list_price = round(kit["ttc"] / (1 + TAX_RATE[kit["tax"]]), 4)

        comp = {}
        for sku, _ in kit["lines"]:
            p = x("product.product", "search_read", [["default_code", "=", sku]], fields=["id"])
            if len(p) != 1:
                raise SystemExit(f"{code}: composant {sku} introuvable ou ambigu ({p})")
            comp[sku] = p[0]["id"]

        tmpl = x("product.template", "search_read",
                 [["default_code", "=", code], ["active", "in", [True, False]]], fields=["id"])
        vals = {
            "type": "consu",
            "is_storable": False,
            "sale_ok": True,
            "purchase_ok": False,
            "available_in_pos": True,
            "categ_id": CATEG_COFFRET,
            "pos_categ_ids": [(6, 0, kit["pos"])],
            "taxes_id": [(6, 0, [kit["tax"]])],
            "list_price": list_price,
            "invoice_policy": "delivery",
        }
        if tmpl:
            tid = tmpl[0]["id"]
            x("product.template", "write", [tid], vals)
            print(f"{code}: template #{tid} existant, mis à jour")
        else:
            tid = x("product.template", "create",
                    {**vals, "name": kit["names"]["fr_BE"], "default_code": code})
            print(f"{code}: template #{tid} créé")
        for lang in LANGS_ORDER:
            x("product.template", "write", [tid], {"name": kit["names"][lang]}, context={"lang": lang})

        bom = x("mrp.bom", "search_read", [["product_tmpl_id", "=", tid]], fields=["id", "type"])
        bom_lines = [(0, 0, {"product_id": comp[sku], "product_qty": q}) for sku, q in kit["lines"]]
        if bom:
            x("mrp.bom", "write", [bom[0]["id"]],
              {"type": "phantom", "bom_line_ids": [(5, 0, 0)] + bom_lines})
            print(f"{code}: BoM #{bom[0]['id']} réécrite en kit")
        else:
            bid = x("mrp.bom", "create", {
                "product_tmpl_id": tid, "type": "phantom", "product_qty": 1,
                "company_id": 1, "bom_line_ids": bom_lines,
            })
            print(f"{code}: BoM kit #{bid} créée")

        # relecture
        for lang in ["fr_BE", "fr_FR", "en_US", "nl_NL"]:
            n = x("product.template", "read", [tid], fields=["name"], context={"lang": lang})[0]["name"]
            print(f"   {lang}: {n}")
        pp = x("product.product", "search_read", [["product_tmpl_id", "=", tid]],
               fields=["id", "display_name", "list_price", "qty_available"], context={"lang": "fr_BE"})[0]
        print(f"   variante #{pp['id']} {pp['display_name']} | HT {pp['list_price']} "
              f"| TTC {pp['list_price'] * (1 + TAX_RATE[kit['tax']]):.2f} | kits dispo (tous entrepôts) {pp['qty_available']}")
        for wid, wname in [(1, "TT"), (3, "LIEGE"), (4, "WAT"), (5, "NAM"), (9, "ROC")]:
            q = x("product.product", "read", [pp["id"]], fields=["qty_available"],
                  context={"warehouse_id": wid})[0]["qty_available"]
            print(f"     {wname}: {q}")


if __name__ == "__main__":
    main()
