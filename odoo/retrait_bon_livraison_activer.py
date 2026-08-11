# -*- coding: utf-8 -*-
"""
Rend visible la carte "Bons de livraison" dans l'apercu Inventaire des magasins.

Une commande de retrait cree un transfert sortant sur le picking type OUT de
l'entrepot du magasin. Quand ce picking type est archive, le transfert existe
mais n'apparait plus dans l'apercu Inventaire : le magasin ne voit pas ses
commandes. C'est le meme correctif que celui pose sur Waterloo (PT#39) le
15/06/2026, applique ici a Liege (PT#25) et Namur (PT#51).

Rien d'autre n'est touche : la route de livraison, la regle pull, la sequence et
le code-barres de ces picking types sont deja actifs et identiques a Waterloo.

Usage :
  python odoo/retrait_bon_livraison_activer.py            # audit
  python odoo/retrait_bon_livraison_activer.py --apply
"""
import argparse
import os
import sys
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"

# picking type OUT -> entrepot
CIBLES = {25: "Magasin Liege", 51: "Magasin Namur"}
REFERENCE = 39  # Waterloo, deja actif : sert de temoin


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


def etat(call):
    ids = sorted(CIBLES) + [REFERENCE]
    pts = call("stock.picking.type", "search_read",
               [["|", ("active", "=", True), ("active", "=", False), ("id", "in", ids)]],
               {"fields": ["id", "name", "active", "warehouse_id", "sequence_code",
                           "barcode", "sequence_id"]})
    for p in sorted(pts, key=lambda x: x["id"]):
        marque = "  (temoin Waterloo)" if p["id"] == REFERENCE else ""
        print(f"  PT#{p['id']:<3} {p['warehouse_id'][1]:<18} {p['name']:<20} "
              f"active={str(p['active']):<5} seq={p['sequence_code']} "
              f"barcode={p['barcode']}{marque}")
    return {p["id"]: p for p in pts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    call = connect()

    print("Etat avant :")
    avant = etat(call)

    a_faire = [i for i in CIBLES if not avant.get(i, {}).get("active", True)]
    if not a_faire:
        print("\n  Rien a faire : les deux picking types sont deja actifs.")
        return
    if not args.apply:
        print(f"\n  A desarchiver : {a_faire}. Ajouter --apply pour executer.")
        return

    call("stock.picking.type", "write", [a_faire, {"active": True}])
    print(f"\n  {len(a_faire)} picking type(s) desarchive(s) : {a_faire}\n")
    print("Etat apres :")
    etat(call)


if __name__ == "__main__":
    sys.exit(main())
