# -*- coding: utf-8 -*-
"""
Force un export de stock COMPLET vers Shopify, toutes locations mappees.

Pourquoi ce script existe : le cron « Shopify Auto Export Stock » (#75) est
INCREMENTAL. Il ne pousse que les produits dont le stock a bouge depuis
`shopify_last_date_update_stock`. Quand on ajoute une nouvelle location au
mapping — Liege et Namur le 10/08/2026 — les articles sans mouvement recent ne
sont jamais mis en file : ils conservent indefiniment la valeur qu'ils avaient
sur Shopify, en l'occurrence celle d'octobre 2025.

Le remede est l'operation « Export Stock » du connecteur avec une date de depart
ancienne, ce que fait ce script via le wizard `shopify.process.import.export`.
C'est l'equivalent exact du bouton de l'interface, pas un contournement.

L'export est idempotent : il repousse vers chaque location la quantite Odoo de
l'entrepot qui lui est mappe. Repousser une valeur deja correcte ne fait rien.

Usage :
  python odoo/shopify_export_stock_complet.py                    # depuis 2024-01-01
  python odoo/shopify_export_stock_complet.py --from 2025-01-01
  python odoo/shopify_export_stock_complet.py --drain 20         # vide la file ensuite
"""
import argparse
import os
import sys
import time
import xmlrpc.client
from collections import Counter

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
INSTANCE = 1
CRON_QUEUE = 62      # Shopify: Process Export Stock Queue


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


def etat_file(call):
    rows = call("shopify.export.stock.queue.line.ept", "read_group",
                [[], ["id"], ["state"]], {"lazy": False})
    return {r["state"]: r["__count"] for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="depuis", default="2024-01-01 00:00:00",
                    help="date de depart de l'export (defaut 2024-01-01)")
    ap.add_argument("--drain", type=int, default=0,
                    help="nb de passes de traitement de file a declencher ensuite")
    args = ap.parse_args()

    call = connect()

    locs = call("shopify.location.ept", "search_read",
                [[("instance_id", "=", INSTANCE)]],
                {"fields": ["id", "name", "export_stock_warehouse_ids"]})
    mappees = [l for l in locs if l["export_stock_warehouse_ids"]]
    print("Locations qui recevront le stock :")
    for l in mappees:
        print(f"  #{l['id']} {l['name'][:44]:<46} entrepot(s) {l['export_stock_warehouse_ids']}")
    non = [l["name"] for l in locs if not l["export_stock_warehouse_ids"]]
    if non:
        print(f"  (non mappees, ignorees : {', '.join(non)})")

    avant = etat_file(call)
    print(f"\nFile avant : {avant}")

    print(f"\nCreation du wizard « Export Stock » depuis {args.depuis} ...")
    wid = call("shopify.process.import.export", "create", [{
        "shopify_instance_id": INSTANCE,
        "shopify_operation": "export_stock",
        "export_stock_from": args.depuis,
    }])
    # Nom de la methode releve sur le bouton de la vue « Process Import/Export »
    # (ir.ui.view #2640) : shopify_execute, et non execute.
    call("shopify.process.import.export", "shopify_execute", [[wid]])
    print(f"  wizard #{wid} execute")

    apres = etat_file(call)
    print(f"File apres : {apres}")
    ajout = apres.get("draft", 0) - avant.get("draft", 0)
    print(f"  -> {ajout:+} lignes en attente de traitement")
    if ajout <= 0:
        print("  ATTENTION : aucune ligne ajoutee. Soit tout est deja a jour, soit la date")
        print("  de depart est trop recente — reessayer avec --from plus ancien.")

    for i in range(args.drain):
        try:
            call("ir.cron", "method_direct_trigger", [[CRON_QUEUE]])
            st = etat_file(call)
            print(f"  passe {i + 1}/{args.drain} : draft={st.get('draft', 0)} "
                  f"done={st.get('done', 0)} failed={st.get('failed', 0)}")
            if not st.get("draft"):
                print("  file vide.")
                break
        except Exception as e:
            print(f"  passe {i + 1} : file en cours de traitement — {str(e)[:90]}")
        time.sleep(20)

    print("\nVerifier ensuite avec odoo/shopify_check_stock_liege_namur.py")


if __name__ == "__main__":
    sys.exit(main())
