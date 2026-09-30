"""
Sortie de stock d'emballages réellement consommés mais jamais déclarés (demande Nicolas 30/09/2026).

  EM0015-EM0017  bobines enveloppes
  EM0034-EM0043  boîtes SRP
  EM0057-EM0060  boîtes packaging Noël
  EM080          boîte calendrier de l'Avent 2025   (demandé « EM0080 », qui n'existe pas)

Méthode : ajustement d'inventaire PUR, quant par quant (inventory_quantity = 0 puis
action_apply_inventory). Contrepartie = emplacement virtuel « Inventory adjustment » (id 14),
jamais un transfert interne. Catégorie en valorisation manuelle (manual_periodic) :
aucune écriture comptable générée.
Garde-fou : quants avec réservation ignorés ; relecture après application.
"""
import os
import sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8")

ODOO_URL = "https://tea-tree.odoo.com"
ODOO_DB = "tsc-be-tea-tree-main-18515272"
ODOO_USER = "nicolas.raes@teatower.com"
ODOO_PWD = os.environ["ODOO_PWD"]
INVENTORY_LOC = 14
REASON = "Consommation emballages non déclarée - sortie 30/09/2026"

CODES = (["EM0015", "EM0016", "EM0017"]
         + [f"EM00{n}" for n in range(34, 44)]
         + [f"EM00{n}" for n in range(57, 61)]
         + ["EM080"])


def main():
    uid = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common").authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)

    def x(model, method, *args, **kw):
        return models.execute_kw(ODOO_DB, uid, ODOO_PWD, model, method, list(args), kw)

    prods = x("product.product", "search_read", [["default_code", "in", CODES]],
              fields=["id", "default_code", "property_stock_inventory"])
    if len(prods) != len(CODES):
        raise SystemExit(f"références manquantes : {set(CODES) - {p['default_code'] for p in prods}}")
    bad = [p["default_code"] for p in prods if not p["property_stock_inventory"]
           or p["property_stock_inventory"][0] != INVENTORY_LOC]
    if bad:
        raise SystemExit(f"contrepartie d'inventaire ≠ {INVENTORY_LOC} : {bad}")

    pids = [p["id"] for p in prods]
    quants = x("stock.quant", "search_read",
               [["product_id", "in", pids], ["location_id.usage", "=", "internal"], ["quantity", "!=", 0]],
               fields=["id", "product_id", "location_id", "quantity", "reserved_quantity"])
    todo = [q for q in quants if not q["reserved_quantity"]]
    for q in quants:
        if q["reserved_quantity"]:
            print(f"IGNORÉ (réservé) {q['product_id'][1]} @ {q['location_id'][1]} rés {q['reserved_quantity']}")

    print(f"{len(todo)} quants à mettre à 0 ({sum(q['quantity'] for q in todo):,.0f} unités)")
    ids = [q["id"] for q in todo]
    if ids:
        x("stock.quant", "write", ids, {"inventory_quantity": 0})
        try:
            x("stock.quant", "action_apply_inventory", ids, context={"inventory_name": REASON})
        except xmlrpc.client.Fault as e:
            if "cannot marshal None" not in str(e):
                raise   # None = succès côté serveur, cf. reference_xmlrpc_odoo_none_marshalling

    for p in sorted(prods, key=lambda p: p["default_code"]):
        q = x("product.product", "read", [p["id"]], fields=["qty_available"])[0]["qty_available"]
        print(f"  {p['default_code']:<7} stock après : {q:,.0f}")


if __name__ == "__main__":
    main()
