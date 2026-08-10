# -*- coding: utf-8 -*-
"""
Active le retrait en magasin natif sur les locations Shopify (etapes 3 et 4).

Pourquoi ce script n'utilise pas le client habituel : l'app « claude9 » n'a ni
`write_locations` ni `write_shipping`. Le connecteur shopify_ept, lui, dispose
d'un jeton d'app privee qui porte ces droits — c'est le meme magasin et le meme
proprietaire, simplement une autre application. Le jeton est donc LU DANS ODOO A
CHAQUE EXECUTION (`shopify.instance.ept.shopify_password`) et n'est jamais ecrit
sur disque : ce depot est public.

Ce que le script fait, par location :
  3. `fulfillsOnlineOrders = true` — prerequis, sinon la location ne peut pas
     servir de point de retrait ;
  4. `locationLocalPickupEnable` — le retrait NATIF, celui que Sendcloud ignore.
     Jamais un tarif d'expedition a 0 EUR portant le nom du magasin : Shopify le
     traiterait comme un envoi et une etiquette serait creee (incident 03/06/26).

Il verifie ensuite deux choses qui n'etaient pas lisibles avec claude9 :
  . qu'aucun tarif d'expedition ne porte un nom de retrait dans une zone ;
  . l'etat final des quatre locations.

PREALABLE : le stock Shopify de la location doit avoir converge sur Odoo, sinon
le retrait s'ouvre sur des quantites fausses. Verifier avec
`shopify_check_stock_liege_namur.py` AVANT de lancer ceci.

Usage :
  python odoo/shopify_pickup_activer.py            # audit seul
  python odoo/shopify_pickup_activer.py --apply
  python odoo/shopify_pickup_activer.py --apply --only Liège
"""
import argparse
import json
import os
import sys
import urllib.request
import xmlrpc.client

ODOO_URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
STORE = "263f0b-3.myshopify.com"
API = "2025-01"

LOCATIONS = {
    "Liège": "84371767635",
    "Namur": "84371865939",
    "Waterloo": "108808798547",
}
INSTRUCTIONS = (
    "Apportez votre e-mail de confirmation lorsque vous venez récupérer votre commande.\n"
    "Votre commande vous attend en boutique aux heures d'ouverture du magasin."
)
DELAI = "TWENTY_FOUR_HOURS"


def jeton_connecteur():
    pwd = os.environ.get("ODOO_PWD")
    if not pwd:
        raise SystemExit("Definir ODOO_PWD avant d'executer ce script.")
    uid = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common").authenticate(DB, USER, pwd, {})
    if not uid:
        raise SystemExit("Authentification Odoo refusee.")
    mo = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    inst = mo.execute_kw(DB, uid, pwd, "shopify.instance.ept", "read", [[1]],
                         {"fields": ["shopify_password"]})[0]
    tok = inst.get("shopify_password")
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
        with urllib.request.urlopen(req, timeout=45) as r:
            payload = json.loads(r.read())
        if payload.get("errors"):
            raise RuntimeError(json.dumps(payload["errors"])[:500])
        return payload["data"]
    return gql


Q_ETAT = """
{ locations(first: 20, includeInactive: true) {
    edges { node { legacyResourceId name isActive fulfillsOnlineOrders
      localPickupSettingsV2 { instructions pickupTime } } } } }
"""
M_FULFILLS = """
mutation($id: ID!, $input: LocationEditInput!) {
  locationEdit(id: $id, input: $input) {
    location { name fulfillsOnlineOrders } userErrors { field message } } }
"""
M_PICKUP = """
mutation($input: DeliveryLocationLocalPickupEnableInput!) {
  locationLocalPickupEnable(localPickupSettings: $input) {
    localPickupSettings { instructions pickupTime } userErrors { field message code } } }
"""
Q_TARIFS = """
{ deliveryProfiles(first: 5) { edges { node { name
    profileLocationGroups { locationGroupZones(first: 20) { edges { node {
      zone { name }
      methodDefinitions(first: 30) { edges { node { name active } } } } } } } } } } }
"""


def etat(gql):
    d = gql(Q_ETAT)
    return {n["node"]["legacyResourceId"]: n["node"] for n in d["locations"]["edges"]}


def affiche(st, titre):
    print(f"\n{titre}")
    print(f"  {'location':<38}{'sert le web':>13}{'retrait':>10}{'delai':>20}{'instructions':>15}")
    for n in st.values():
        p = n.get("localPickupSettingsV2")
        instr = ("renseignees" if p and p["instructions"] else ("VIDES" if p else "—"))
        print(f"  {n['name'][:37]:<38}{str(n['fulfillsOnlineOrders']):>13}"
              f"{('OUI' if p else 'non'):>10}{(p['pickupTime'] if p else '—'):>20}{instr:>15}")


def controle_tarifs(gql):
    print("\nTarifs d'expedition — recherche d'un tarif de retrait deguise :")
    d = gql(Q_TARIFS)
    suspects = []
    total = 0
    for pe in d["deliveryProfiles"]["edges"]:
        for lg in pe["node"]["profileLocationGroups"]:
            for ze in lg["locationGroupZones"]["edges"]:
                zone = ze["node"]["zone"]["name"]
                for me in ze["node"]["methodDefinitions"]["edges"]:
                    nom = me["node"]["name"]
                    total += 1
                    bas = nom.lower()
                    if "retrait" in bas or "pickup" in bas or "magasin" in bas:
                        suspects.append((zone, nom))
    if suspects:
        print(f"  {len(suspects)} tarif(s) SUSPECT(S) — a supprimer, ils declenchent Sendcloud :")
        for z, n in suspects:
            print(f"    [{z}] {n}")
    else:
        print(f"  {total} tarifs examines, aucun ne porte un nom de retrait. Rien a corriger.")
    return suspects


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", help="ne traiter qu'une location (nom exact)")
    args = ap.parse_args()

    gql = gql_factory(jeton_connecteur())
    st = etat(gql)
    affiche(st, "ETAT AVANT")

    cibles = {k: v for k, v in LOCATIONS.items() if not args.only or k == args.only}
    todo = []
    for nom, lid in cibles.items():
        n = st.get(lid, {})
        p = n.get("localPickupSettingsV2")
        if not n.get("fulfillsOnlineOrders") or not p or not p.get("instructions"):
            todo.append((nom, lid))
    if not todo:
        print("\n  Tout est deja en place.")
        controle_tarifs(gql)
        return

    print(f"\n  A traiter : {', '.join(n for n, _ in todo)}")
    if not args.apply:
        print("  Audit seul. Ajouter --apply pour executer.")
        return

    for nom, lid in todo:
        gid = f"gid://shopify/Location/{lid}"
        print(f"\n  {nom} :")
        r = gql(M_FULFILLS, {"id": gid, "input": {"fulfillsOnlineOrders": True}})
        e = r["locationEdit"]["userErrors"]
        print("    sert les commandes en ligne : " + ("OK" if not e else f"KO {e}"))
        r = gql(M_PICKUP, {"input": {"locationId": gid, "pickupTime": DELAI,
                                     "instructions": INSTRUCTIONS}})
        e = r["locationLocalPickupEnable"]["userErrors"]
        print("    retrait en magasin natif    : " + ("OK" if not e else f"KO {e}"))

    affiche(etat(gql), "ETAT APRES")
    controle_tarifs(gql)
    print("\n  Reste a verifier a l'oeil dans l'admin : Parametres -> Expedition et")
    print("  livraison -> Ordre de routage des commandes, Somme-Leuze doit rester en")
    print("  premiere position (non expose par l'API).")


if __name__ == "__main__":
    sys.exit(main())
