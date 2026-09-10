# -*- coding: utf-8 -*-
"""C0195 Calendrier de l'avent 2026 : 9 pieces par magasin.

Schema repris des reappros existants (« Transfert exceptionnel magasins »):
un picking par magasin, type « <Magasin>: Transferts internes », source forcee
sur TT/Stock (le type propose par defaut le stock du magasin lui-meme).

Le stock est a 0 : les 2.500 pieces arrivent par TT/IN/00621 (PO P00447, Les
Ateliers Saupont). Les transferts sont donc crees et confirmes, PAS valides :
ils se reserveront tout seuls a la reception.
"""
import os, sys, xmlrpc.client
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
uid = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def c(mo, me, a, k=None):
    return _m.execute_kw(DB, uid, PWD, mo, me, a, k or {})


PRODUIT = 7658            # C0195 Calendrier de l'avent 2026
QTE = 9.0
SRC = 4507                # TT/Stock -- resolu plus bas, valeur de secours
ORIGINE = "Calendriers de l'avent 2026 - dotation magasins"
DATE = "2026-09-10 08:00:00"

MAGASINS = [
    ("Magasin Liège",    30, "LIEGE/Stock"),
    ("Magasin Waterloo", 44, "WAT/Stock"),
    ("Magasin Namur",    56, "NAM/Stock"),
    ("Magasin Rocourt", 104, "ROC/Stock"),
]

SRC = c("stock.location", "search", [[["complete_name", "=", "TT/Stock"]]])[0]
prod = c("product.product", "read", [[PRODUIT]], {"fields": ["default_code", "name", "uom_id"]})[0]
print("produit : [%s] %s | source : TT/Stock (#%d)" % (prod["default_code"], prod["name"], SRC))

for nom, ptype, dest_name in MAGASINS:
    dest = c("stock.location", "search", [[["complete_name", "=", dest_name]]])[0]

    # idempotence : ne pas recreer si le transfert existe deja
    deja = c("stock.picking", "search_read",
             [[["picking_type_id", "=", ptype], ["origin", "=", ORIGINE],
               ["state", "not in", ["cancel"]]]], {"fields": ["name", "state"]})
    if deja:
        print("  %-18s deja cree : %s (%s)" % (nom, deja[0]["name"], deja[0]["state"]))
        continue

    pid = c("stock.picking", "create", [{
        "picking_type_id": ptype,
        "location_id": SRC,
        "location_dest_id": dest,
        "scheduled_date": DATE,
        "origin": ORIGINE,
        "move_ids_without_package": [(0, 0, {
            "name": prod["name"],
            "product_id": PRODUIT,
            "product_uom_qty": QTE,
            "product_uom": prod["uom_id"][0],
            "location_id": SRC,
            "location_dest_id": dest,
        })],
    }])
    c("stock.picking", "action_confirm", [[pid]])
    p = c("stock.picking", "read", [[pid]], {"fields": ["name", "state"]})[0]
    print("  %-18s -> %-18s %s" % (nom, p["name"], p["state"]))

print("\n" + "=" * 78 + "\nRELECTURE\n" + "=" * 78)
tot = 0.0
for p in c("stock.picking", "search_read", [[["origin", "=", ORIGINE]]],
           {"fields": ["name", "state", "location_id", "location_dest_id", "scheduled_date"],
            "order": "name"}):
    mv = c("stock.move", "search_read", [[["picking_id", "=", p["id"]]]],
           {"fields": ["product_uom_qty", "forecast_availability"]})
    q = sum(x["product_uom_qty"] for x in mv)
    tot += q
    print("  %-18s %-10s %-12s -> %-14s q %4.0f  prevu %s"
          % (p["name"], p["state"], p["location_id"][1], p["location_dest_id"][1],
             q, p["scheduled_date"][:10]))
print("  TOTAL sorti de TT/Stock : %.0f pieces" % tot)

d = c("product.product", "read", [[PRODUIT]], {"fields": ["qty_available", "virtual_available",
                                                          "outgoing_qty", "incoming_qty"]})[0]
print("\n  C0195 : en stock %.0f | attendu %.0f | sorties reservees %.0f | previsionnel %.0f"
      % (d["qty_available"], d["incoming_qty"], d["outgoing_qty"], d["virtual_available"]))
