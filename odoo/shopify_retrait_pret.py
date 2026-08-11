# -*- coding: utf-8 -*-
"""
Marque la commande « prete pour le retrait » dans Shopify quand le magasin
valide son bon de livraison dans Odoo.

Le geste existait deja, mais a la main : le 10/08, le bon WAT/OUT/00012 est
valide a 13:40:01 dans Odoo et l'e-mail « ready for pickup » part a 13:40:21
depuis l'application mobile Shopify. Vingt secondes d'ecart, deux saisies. Ce
script supprime la seconde.

Pourquoi Shopify et pas un e-mail maison : c'est Shopify qui connait l'adresse
du point de retrait, ses horaires et les instructions saisies par magasin, et
c'est lui qui bascule la commande dans l'etat « prete » visible cote client.

Chaine :
  1. Odoo — bons de livraison VALIDES des trois magasins (picking types 25
     Liege, 39 Waterloo, 51 Namur), rattaches a une commande Shopify, pas
     encore traites (champ `x_shopify_pret`) ;
  2. Shopify — on retrouve le fulfillment order de type PICK_UP de la commande
     et on appelle `fulfillmentOrderLineItemsPreparedForPickup`, qui declenche
     l'e-mail « votre commande est prete » ;
  3. retour dans Odoo — le bon est marque, il ne sera jamais retraite.

Trois garde-fous, parce qu'un e-mail client ne se rattrape pas :
  . une fenetre de N jours (5 par defaut) — un vieux bon revalide ne reveille
    pas une commande de juillet ;
  . l'etat du fulfillment order cote Shopify — seul un `OPEN` est marque ;
    `IN_PROGRESS` signifie deja pret, on se contente de poser le drapeau ;
  . le drapeau Odoo, qui rend l'execution idempotente.

Le jeton Shopify est celui du connecteur shopify_ept, LU DANS ODOO a chaque
execution et jamais ecrit sur disque : ce depot est public. L'app « claude9 »
n'a pas les droits fulfillment, celle du connecteur si.

Usage :
  python odoo/shopify_retrait_pret.py                 # audit, n'ecrit rien
  python odoo/shopify_retrait_pret.py --apply
  python odoo/shopify_retrait_pret.py --fenetre 10 --apply
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import xmlrpc.client
from datetime import datetime, timedelta, timezone

ODOO_URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
STORE = "263f0b-3.myshopify.com"
API = "2025-01"

PICKING_TYPES = {25: "Liege", 39: "Waterloo", 51: "Namur"}
CHAMP = "x_shopify_pret"
FENETRE_JOURS = 5

MUTATION = """
mutation($input: FulfillmentOrderLineItemsPreparedForPickupInput!) {
  fulfillmentOrderLineItemsPreparedForPickup(input: $input) {
    userErrors { field message }
  }
}
"""

REQUETE_COMMANDE = """
query($id: ID!) {
  order(id: $id) {
    name
    displayFulfillmentStatus
    fulfillmentOrders(first: 10) {
      nodes {
        id
        status
        deliveryMethod { methodType }
        assignedLocation { name }
      }
    }
  }
}
"""


# --------------------------------------------------------------------------- Odoo
def odoo():
    pwd = os.environ.get("ODOO_PWD")
    if not pwd:
        raise SystemExit("Definir ODOO_PWD avant d'executer ce script.")
    uid = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common").authenticate(DB, USER, pwd, {})
    if not uid:
        raise SystemExit("Authentification Odoo refusee.")
    mo = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

    def call(model, method, args, kw=None):
        return mo.execute_kw(DB, uid, pwd, model, method, args, kw or {})

    return call


def assurer_champ(call, ecrire):
    """Le drapeau d'idempotence. Cree au premier --apply."""
    if call("ir.model.fields", "search_count",
            [[("model", "=", "stock.picking"), ("name", "=", CHAMP)]]):
        return True
    if not ecrire:
        print(f"  (le champ {CHAMP} sera cree au premier --apply)")
        return False
    mid = call("ir.model", "search", [[("model", "=", "stock.picking")]])[0]
    call("ir.model.fields", "create", [{
        "model_id": mid, "name": CHAMP, "ttype": "boolean",
        "field_description": "Shopify prevenu (retrait pret)",
        "state": "manual", "store": True,
    }])
    print(f"  champ {CHAMP} cree sur stock.picking")
    return True


def candidats(call, fenetre, champ_present):
    # Odoo stocke date_done en UTC naif : on compare donc en UTC.
    depuis = (datetime.now(timezone.utc) - timedelta(days=fenetre)).strftime("%Y-%m-%d %H:%M:%S")
    domaine = [("picking_type_id", "in", list(PICKING_TYPES)),
               ("state", "=", "done"),
               ("date_done", ">=", depuis)]
    if champ_present:
        domaine.append((CHAMP, "=", False))
    pk = call("stock.picking", "search_read", [domaine],
              {"fields": ["id", "name", "date_done", "sale_id", "picking_type_id"],
               "order": "date_done"})
    sortie = []
    for p in pk:
        if not p["sale_id"]:
            continue
        so = call("sale.order", "read", [[p["sale_id"][0]]],
                  {"fields": ["name", "shopify_order_id", "partner_id"]})[0]
        if not so.get("shopify_order_id"):
            continue
        p["so"] = so
        sortie.append(p)
    return sortie


# ------------------------------------------------------------------------ Shopify
def jeton(call):
    tok = call("shopify.instance.ept", "read", [[1]],
               {"fields": ["shopify_password"]})[0].get("shopify_password")
    if not tok:
        raise SystemExit("Aucun jeton Shopify sur l'instance shopify_ept #1.")
    return tok


def gql_factory(token):
    def gql(query, variables=None):
        body = json.dumps({"query": query,
                           **({"variables": variables} if variables else {})}).encode()
        req = urllib.request.Request(f"https://{STORE}/admin/api/{API}/graphql.json",
                                     data=body, method="POST")
        req.add_header("X-Shopify-Access-Token", token)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
        except urllib.error.HTTPError as e:
            raise SystemExit(f"Shopify HTTP {e.code} : {e.read()[:400]!r}")
        if d.get("errors"):
            raise SystemExit(f"Shopify GraphQL : {json.dumps(d['errors'])[:400]}")
        return d["data"]
    return gql


def fo_retrait(gql, shopify_order_id):
    """Le fulfillment order de retrait de la commande, ou None."""
    d = gql(REQUETE_COMMANDE, {"id": f"gid://shopify/Order/{shopify_order_id}"})
    cmd = d.get("order")
    if not cmd:
        return None, None
    for fo in cmd["fulfillmentOrders"]["nodes"]:
        methode = (fo.get("deliveryMethod") or {}).get("methodType")
        if methode == "PICK_UP":
            return cmd, fo
    return cmd, None


def marquer_pret(gql, fo_id):
    d = gql(MUTATION, {"input": {"lineItemsByFulfillmentOrder": [
        {"fulfillmentOrderId": fo_id}]}})
    erreurs = d["fulfillmentOrderLineItemsPreparedForPickup"]["userErrors"]
    if erreurs:
        raise RuntimeError(json.dumps(erreurs))


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="sans quoi rien n'est ecrit")
    ap.add_argument("--fenetre", type=int, default=FENETRE_JOURS,
                    help="anciennete maximale d'un bon de livraison, en jours")
    args = ap.parse_args()

    call = odoo()
    champ_present = assurer_champ(call, args.apply)
    liste = candidats(call, args.fenetre, champ_present)

    if not liste:
        print(f"  Rien a traiter (fenetre {args.fenetre} j).")
        return

    gql = gql_factory(jeton(call))
    faits = ignores = echecs = 0

    for p in liste:
        etiquette = (f"{p['name']} — {PICKING_TYPES.get(p['picking_type_id'][0], '?')} — "
                     f"{p['so']['name']} — {p['so']['partner_id'][1]}")
        cmd, fo = fo_retrait(gql, p["so"]["shopify_order_id"])
        if cmd is None:
            print(f"  ! {etiquette} : commande introuvable cote Shopify")
            echecs += 1
            continue
        if fo is None:
            print(f"  - {etiquette} : aucun retrait cote Shopify, ignore")
            ignores += 1
            continue

        if fo["status"] != "OPEN":
            print(f"  = {etiquette} : deja {fo['status']} cote Shopify, rien a envoyer")
            ignores += 1
            if args.apply:
                call("stock.picking", "write", [[p["id"]], {CHAMP: True}])
            continue

        if not args.apply:
            print(f"  → {etiquette} : serait marque pret ({fo['assignedLocation']['name']})")
            continue

        try:
            marquer_pret(gql, fo["id"])
        except RuntimeError as e:
            print(f"  ! {etiquette} : refus Shopify {e}")
            echecs += 1
            continue
        call("stock.picking", "write", [[p["id"]], {CHAMP: True}])
        print(f"  ✓ {etiquette} : client prevenu par Shopify")
        faits += 1

    if args.apply:
        print(f"\n  {faits} client(s) prevenu(s), {ignores} ignore(s), {echecs} echec(s)")
    else:
        print(f"\n  Audit seul — {len(liste)} bon(s) dans la fenetre. "
              f"Ajouter --apply pour envoyer.")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
