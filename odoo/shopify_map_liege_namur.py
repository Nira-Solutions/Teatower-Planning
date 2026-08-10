# -*- coding: utf-8 -*-
"""
Mappe les locations Shopify Liege et Namur vers leurs entrepots Odoo, sur le
modele de ce qui a ete fait pour Waterloo le 04/06/2026.

Contexte : le retrait en magasin Shopify->Odoo fonctionne a Waterloo. Pour
l'ouvrir a Liege et Namur il faut quatre choses, dont ce script fait la
premiere :

  1. [CE SCRIPT] cote Odoo, mapper `shopify.location.ept` -> `stock.warehouse`
     (export du stock, entrepot de la commande, entrepot d'import) ;
  2. l'export de stock doit tourner et faire converger Shopify sur Odoo ;
  3. cote Shopify, la location doit remplir les commandes en ligne
     (`fulfillsOnlineOrders`) ;
  4. cote Shopify, le retrait en magasin natif doit etre active sur la location.

Les points 3 et 4 exigent le scope `write_locations`, que l'app claude9 n'a pas :
ils se font dans l'admin Shopify (ou apres ajout du scope).

ORDRE IMPERATIF — 1 et 2 AVANT 3 et 4. Le stock affiche par Shopify sur Liege et
Namur date d'octobre 2025 : ouvrir le retrait avant d'avoir reexporte ferait
vendre sur des quantites vieilles de dix mois.

Usage :
  python odoo/shopify_map_liege_namur.py            # audit seul, n'ecrit rien
  python odoo/shopify_map_liege_namur.py --apply    # applique le mapping
  python odoo/shopify_map_liege_namur.py --revert   # remet les deux locations a vide
"""
import argparse
import os
import sys
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"

# location Shopify (shopify.location.ept) -> entrepot Odoo (stock.warehouse)
MAPPING = {
    1: (3, "Liège", "Magasin Liège (LIEGE)"),
    2: (5, "Namur", "Magasin Namur (NAM)"),
}
REFERENCE = 4      # Waterloo, le mapping deja valide qui sert de gabarit


def connect():
    pwd = os.environ.get("ODOO_PWD")
    if not pwd:
        raise SystemExit("Definir ODOO_PWD avant d'executer ce script.")
    uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, pwd, {})
    if not uid:
        raise SystemExit("Authentification Odoo refusee.")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    def call(model, method, args, kw=None):
        return models.execute_kw(DB, uid, pwd, model, method, args, kw or {})

    return call


FIELDS = ["id", "name", "shopify_location_id", "is_primary_location",
          "export_stock_warehouse_ids", "import_stock_warehouse_id",
          "warehouse_for_order"]


def show(call, titre):
    print(f"\n{titre}")
    print(f"  {'id':<4}{'location Shopify':<38}{'export':<12}{'import':<22}{'commande':<22}")
    for l in call("shopify.location.ept", "search_read", [[]], {"fields": FIELDS}):
        exp = ",".join(str(x) for x in l["export_stock_warehouse_ids"]) or "—"
        imp = l["import_stock_warehouse_id"][1] if l["import_stock_warehouse_id"] else "—"
        cmd = l["warehouse_for_order"][1] if l["warehouse_for_order"] else "—"
        flag = " *primaire" if l["is_primary_location"] else ""
        print(f"  {l['id']:<4}{(l['name'] + flag)[:37]:<38}{exp:<12}{imp:<22}{cmd:<22}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--revert", action="store_true")
    args = ap.parse_args()

    call = connect()

    inst = call("shopify.instance.ept", "read", [[1]],
                {"fields": ["name", "is_delivery_multi_warehouse", "shopify_warehouse_id"]})[0]
    print(f"Instance : {inst['name']}")
    print(f"  is_delivery_multi_warehouse = {inst['is_delivery_multi_warehouse']}"
          f"   (sans ce drapeau, warehouse_for_order est IGNORE)")
    print(f"  entrepot par defaut = {inst['shopify_warehouse_id'][1]}")
    if not inst["is_delivery_multi_warehouse"]:
        raise SystemExit("is_delivery_multi_warehouse est False — le mapping par location "
                         "serait sans effet. Activer d'abord ce drapeau sur l'instance.")

    ref = call("shopify.location.ept", "read", [[REFERENCE]], {"fields": FIELDS})[0]
    print(f"\nGabarit de reference — location #{REFERENCE} « {ref['name']} » :")
    print(f"  export  = {ref['export_stock_warehouse_ids']}")
    print(f"  import  = {ref['import_stock_warehouse_id']}")
    print(f"  commande= {ref['warehouse_for_order']}")

    show(call, "ETAT ACTUEL")

    if not (args.apply or args.revert):
        print("\nAudit seul — rien n'a ete ecrit. Ajouter --apply pour appliquer le mapping.")
        return

    if args.revert:
        for lid in MAPPING:
            call("shopify.location.ept", "write", [[lid], {
                "export_stock_warehouse_ids": [(5, 0, 0)],
                "import_stock_warehouse_id": False,
                "warehouse_for_order": False,
            }])
            print(f"  location #{lid} remise a vide")
        show(call, "ETAT APRES REVERT")
        return

    # Verification des entrepots cibles avant ecriture
    wh_ids = [w for w, _, _ in MAPPING.values()]
    whs = {w["id"]: w for w in call("stock.warehouse", "read", [wh_ids],
                                    {"fields": ["id", "name", "code", "delivery_steps", "active"]})}
    for lid, (wid, nom, lib) in MAPPING.items():
        w = whs.get(wid)
        if not w or not w["active"]:
            raise SystemExit(f"Entrepot {wid} introuvable ou archive — mapping annule.")
        if w["delivery_steps"] != "ship_only":
            print(f"  ATTENTION : {w['name']} est en '{w['delivery_steps']}' et non 'ship_only' ; "
                  f"le retrait creera plus d'une operation.")

    print()
    for lid, (wid, nom, lib) in MAPPING.items():
        call("shopify.location.ept", "write", [[lid], {
            "export_stock_warehouse_ids": [(6, 0, [wid])],
            "import_stock_warehouse_id": wid,
            "warehouse_for_order": wid,
        }])
        print(f"  location #{lid} « {nom} »  ->  {lib}")

    show(call, "ETAT APRES APPLICATION")

    print("\nSuite des operations :")
    print("  . le cron #75 « Shopify Auto Export Stock » (15 min) va pousser le stock")
    print("    Odoo de LIEGE et NAM vers les locations Shopify correspondantes ;")
    print("  . le cron #62 « Process Export Stock Queue » (15 min) traite la file ;")
    print("  . verifier la convergence avec odoo/shopify_check_stock_liege_namur.py")
    print("    AVANT d'activer le retrait en magasin cote Shopify.")


if __name__ == "__main__":
    sys.exit(main())
