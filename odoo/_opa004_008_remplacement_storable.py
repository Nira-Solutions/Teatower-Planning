"""
OPA004-OPA008 (Oxyprolane, fournisseur Pharma Recherche) créés le 14/09/2026 SANS suivi
d'inventaire, puis réceptionnés le 15/09 (P00619, TT/IN/00935 + TT/STOR/00868).
Les lignes de mouvement `done` verrouillent is_storable à vie → procédure de remplacement
(cf. mémoire reference_odoo_is_storable_verrou) :

 1. Ancien template : code suffixé -HIST, EAN vidé, ni vendable ni achetable.
 2. Nouveau template au vrai code + EAN, is_storable=True, config et fournisseurs recopiés,
    nom écrit dans les 4 langues.
 3. Brouillons TT/INT/00426 et 00427 (OPA004, qté 0) annulés.
 4. Ajustement d'inventaire = quantités réceptionnées, dans l'emplacement de rangement.
    Catégorie Opalya en inventaire périodique → aucune écriture comptable.

Idempotent. Sans --apply : simulation. Mot de passe lu dans ODOO_PWD (dépôt public).
"""
import os
import sys
import xmlrpc.client

APPLY = "--apply" in sys.argv
URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
PWD = os.environ["ODOO_PWD"]
LANGS = ["fr_BE", "fr_FR", "en_US", "nl_NL"]
CODES = ["OPA004", "OPA005", "OPA006", "OPA007", "OPA008"]
DRAFTS = ["TT/INT/00426", "TT/INT/00427"]
COPY = ["name", "list_price", "standard_price", "categ_id", "uom_id", "uom_po_id", "taxes_id",
        "supplier_taxes_id", "route_ids", "invoice_policy", "purchase_method", "responsible_id",
        "tracking", "available_in_pos", "type", "weight", "description_sale", "description_purchase"]

uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, "nicolas.raes@teatower.com", PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def x(model, method, args, kw=None):
    return models.execute_kw(DB, uid, PWD, model, method, args, kw or {})


def m2o(v):
    return v[0] if isinstance(v, list) else v


def received_by_location(variant_id):
    """Solde net par emplacement interne des mouvements done (réception puis rangement)."""
    lines = x("stock.move.line", "search_read",
              [[["product_id", "=", variant_id], ["state", "=", "done"]]],
              {"fields": ["location_id", "location_dest_id", "quantity"]})
    internal = set(x("stock.location", "search", [[["usage", "=", "internal"]]]))
    net = {}
    for l in lines:
        src, dst = l["location_id"][0], l["location_dest_id"][0]
        if dst in internal:
            net[dst] = net.get(dst, 0) + l["quantity"]
        if src in internal:
            net[src] = net.get(src, 0) - l["quantity"]
    return {loc: q for loc, q in net.items() if q > 0}


def main():
    for p in x("stock.picking", "search_read", [[["name", "in", DRAFTS], ["state", "=", "draft"]]],
               {"fields": ["name"]}):
        print(f"[draft] annulation {p['name']}")
        if APPLY:
            try:
                x("stock.picking", "action_cancel", [[p["id"]]])
            except xmlrpc.client.Fault as e:
                if "marshal None" not in str(e):
                    raise

    for code in CODES:
        new = x("product.template", "search_read", [[["default_code", "=", code], ["is_storable", "=", True]]],
                {"fields": ["id"]})
        old = x("product.template", "search_read",
                [[["default_code", "in", [code, f"{code}-HIST"]], ["is_storable", "=", False]]],
                {"fields": COPY + ["id", "barcode", "seller_ids", "sale_ok", "purchase_ok"],
                 "context": {"active_test": False}})
        if not old:
            print(f"[{code}] ancien template introuvable")
            continue
        old = old[0]
        old_variant = x("product.product", "search", [[["product_tmpl_id", "=", old["id"]]]],
                        {"context": {"active_test": False}})[0]
        stock = received_by_location(old_variant)
        barcode = old["barcode"]
        print(f"[{code}] ancien tmpl {old['id']} — réceptionné {stock}")

        if not APPLY:
            continue

        if old["barcode"] or old.get("sale_ok") or old.get("purchase_ok"):
            x("product.template", "write", [[old["id"]], {
                "default_code": f"{code}-HIST", "barcode": False, "sale_ok": False, "purchase_ok": False}])

        if new:
            tid = new[0]["id"]
            print(f"[{code}] nouveau template déjà créé ({tid})")
        else:
            vals = {k: m2o(old[k]) for k in COPY if k not in ("taxes_id", "supplier_taxes_id", "route_ids")}
            vals.update({
                "default_code": code, "barcode": barcode, "is_storable": True,
                "sale_ok": True, "purchase_ok": True,
                "taxes_id": [(6, 0, old["taxes_id"])],
                "supplier_taxes_id": [(6, 0, old["supplier_taxes_id"])],
                "route_ids": [(6, 0, old["route_ids"])],
            })
            sellers = x("product.supplierinfo", "read", [old["seller_ids"]],
                        {"fields": ["partner_id", "product_code", "product_name", "price", "min_qty",
                                    "delay", "currency_id"]})
            vals["seller_ids"] = [(0, 0, {k: m2o(s[k]) for k in s if k != "id"}) for s in sellers]
            tid = x("product.template", "create", [vals])
            print(f"[{code}] nouveau template {tid} (suivi d'inventaire)")
        for lang in LANGS:
            x("product.template", "write", [[tid], {"name": old["name"]}], {"context": {"lang": lang}})

        variant = x("product.product", "search", [[["product_tmpl_id", "=", tid]]])[0]
        for loc, qty in stock.items():
            quant = x("stock.quant", "search_read", [[["product_id", "=", variant], ["location_id", "=", loc]]],
                      {"fields": ["id", "quantity"]})
            if quant and quant[0]["quantity"] >= qty:
                print(f"[{code}] stock déjà présent en {loc} ({quant[0]['quantity']})")
                continue
            ctx = {"context": {"inventory_mode": True}}
            if quant:
                qid = quant[0]["id"]
                x("stock.quant", "write", [[qid], {"inventory_quantity": qty}], ctx)
            else:
                qid = x("stock.quant", "create", [{"product_id": variant, "location_id": loc,
                                                    "inventory_quantity": qty}], ctx)
            try:
                x("stock.quant", "action_apply_inventory", [[qid]])
            except xmlrpc.client.Fault as e:
                if "marshal None" not in str(e):
                    raise
            print(f"[{code}] inventaire +{qty} en emplacement {loc}")


if __name__ == "__main__":
    main()
