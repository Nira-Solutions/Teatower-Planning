# -*- coding: utf-8 -*-
"""
Active le retrait en magasin natif sur les locations Shopify Liege et Namur.

Etape 3 et 4 de l'ouverture du retrait (les etapes 1 et 2 sont dans
`shopify_map_liege_namur.py` puis `shopify_check_stock_liege_namur.py`) :

  3. `fulfillsOnlineOrders = true` — sans quoi la location ne peut pas servir de
     point de retrait ;
  4. retrait en magasin natif, avec instructions et delai de preparation.

Le retrait doit imperativement etre le RETRAIT NATIF, jamais un tarif
d'expedition a 0 EUR portant le nom du magasin : Shopify traiterait alors la
commande comme un envoi et Sendcloud creerait une etiquette. Incident constate
le 03/06/2026 sur Waterloo.

PREREQUIS DE DROITS — verifie le 10/08/2026, l'app « claude9 » n'a NI l'un NI
l'autre des deux scopes necessaires, qui sont distincts :
  . `write_locations`  pour `fulfillsOnlineOrders` (mutation locationEdit) ;
  . `write_shipping`   pour le retrait natif (mutation locationLocalPickupEnable,
                       qui accepte aussi la permission `manage_delivery_settings`).
En l'etat ce script echoue proprement en signalant ce qui manque. Deux voies :
  a. ajouter les deux scopes a l'app dans l'admin Shopify, puis le relancer ;
  b. ou faire les quatre reglages a la main dans l'admin — le script affiche
     alors exactement quoi cocher.

ATTENTION APRES ACTIVATION : une location qui remplit les commandes en ligne
devient eligible au routage des commandes normales. Verifier dans
Parametres -> Expedition et livraison -> Ordre de routage que Somme-Leuze reste
prioritaire, sinon des commandes Bpost pourraient etre affectees a un magasin.

Usage :
  python odoo/shopify_pickup_liege_namur.py            # audit + mode d'emploi
  python odoo/shopify_pickup_liege_namur.py --apply    # tente l'activation
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from shopify_client import shopify  # noqa: E402

CIBLES = {
    "Liège": "84371767635",
    "Namur": "84371865939",
}
TEMOIN = ("Waterloo", "108808798547")

INSTRUCTIONS = (
    "Apportez votre e-mail de confirmation lorsque vous venez récupérer votre commande.\n"
    "Votre commande vous attend en boutique aux heures d'ouverture du magasin."
)
DELAI = "TWENTY_FOUR_HOURS"   # meme delai que Waterloo et Somme-Leuze

Q_ETAT = """
{ locations(first: 20, includeInactive: true) {
    edges { node { legacyResourceId name isActive fulfillsOnlineOrders
      localPickupSettingsV2 { instructions pickupTime }
      address { city zip } } } } }
"""

M_FULFILLS = """
mutation($id: ID!, $input: LocationEditInput!) {
  locationEdit(id: $id, input: $input) {
    location { legacyResourceId name fulfillsOnlineOrders }
    userErrors { field message } } }
"""

# Nom du type verifie par introspection sur l'API 2025-01 : c'est bien
# DeliveryLocationLocalPickupEnableInput, et non LocationLocalPickupEnableInput.
M_PICKUP = """
mutation($input: DeliveryLocationLocalPickupEnableInput!) {
  locationLocalPickupEnable(localPickupSettings: $input) {
    localPickupSettings { instructions pickupTime }
    userErrors { field message code } } }
"""


def etat():
    d = shopify.graphql(Q_ETAT)
    return {n["node"]["legacyResourceId"]: n["node"]
            for n in d["locations"]["edges"]}


def affiche(st, titre):
    print(f"\n{titre}")
    print(f"  {'location':<38}{'active':>8}{'sert le web':>13}{'retrait natif':>16}{'delai':>22}")
    for lid, n in st.items():
        p = n.get("localPickupSettingsV2")
        print(f"  {n['name'][:37]:<38}{str(n['isActive']):>8}"
              f"{str(n['fulfillsOnlineOrders']):>13}"
              f"{('OUI' if p else 'non'):>16}"
              f"{(p['pickupTime'] if p else '—'):>22}")


def mode_emploi():
    print("""
  MODE D'EMPLOI MANUEL — admin Shopify, a faire une fois par magasin

  1. Parametres -> Emplacements -> « Liege » (puis « Namur »)
     cocher « Cet emplacement execute les commandes en ligne ».

  2. Parametres -> Expedition et livraison -> Modes de livraison supplementaires
     -> Retrait en magasin -> selectionner l'emplacement -> Activer.
     Delai de preparation : « Habituellement pret en 24 heures ».
     Instructions a coller :

       Apportez votre e-mail de confirmation lorsque vous venez recuperer
       votre commande.
       Votre commande vous attend en boutique aux heures d'ouverture du magasin.

  3. Dans la meme page, verifier qu'AUCUN tarif d'expedition ne s'appelle
     « Retrait en magasin a Liege / Namur » dans la zone Belgique. Si un tel
     tarif existe, le supprimer : c'est lui qui declenche une etiquette
     Sendcloud a tort. Les tarifs Bpost Home et Point relais restent.

  4. Parametres -> Expedition et livraison -> Ordre de routage des commandes :
     verifier que « Somme-Leuze » reste en premiere position.

  5. Tant qu'a faire : Waterloo a des instructions de retrait VIDES depuis le
     04/06/2026. Y coller le meme texte qu'au point 2.
""")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    st = etat()
    affiche(st, "ETAT ACTUEL DES LOCATIONS")

    t = st.get(TEMOIN[1])
    if t:
        p = t.get("localPickupSettingsV2")
        print(f"\n  Temoin — {TEMOIN[0]} : sert le web = {t['fulfillsOnlineOrders']}, "
              f"retrait natif = {'OUI' if p else 'non'}"
              f"{', instructions VIDES' if p and not p['instructions'] else ''}")

    a_faire = [(nom, lid) for nom, lid in CIBLES.items()
               if not st.get(lid, {}).get("fulfillsOnlineOrders")
               or not st.get(lid, {}).get("localPickupSettingsV2")]
    if not a_faire:
        print("\n  Liege et Namur sont deja configures — rien a faire.")
        return

    print(f"\n  A configurer : {', '.join(n for n, _ in a_faire)}")

    if not args.apply:
        print("\n  Audit seul. Ajouter --apply pour tenter l'activation par l'API.")
        mode_emploi()
        return

    echec_droits = False
    for nom, lid in a_faire:
        gid = f"gid://shopify/Location/{lid}"
        print(f"\n  {nom} :")
        try:
            r = shopify.graphql(M_FULFILLS, {"id": gid, "input": {"fulfillsOnlineOrders": True}})
            errs = r["locationEdit"]["userErrors"]
            print("    sert les commandes en ligne : "
                  + ("OK" if not errs else f"KO — {errs}"))
        except RuntimeError as e:
            echec_droits = True
            print(f"    sert les commandes en ligne : REFUSE — {str(e)[:180]}")
        try:
            r = shopify.graphql(M_PICKUP, {"input": {
                "locationId": gid, "pickupTime": DELAI, "instructions": INSTRUCTIONS}})
            errs = r["locationLocalPickupEnable"]["userErrors"]
            print("    retrait en magasin natif    : "
                  + ("OK" if not errs else f"KO — {errs}"))
        except RuntimeError as e:
            echec_droits = True
            print(f"    retrait en magasin natif    : REFUSE — {str(e)[:180]}")

    affiche(etat(), "ETAT APRES TENTATIVE")
    if echec_droits:
        print("\n  L'app claude9 n'a pas les droits d'ecriture sur les emplacements.")
        print("  Ajouter `write_locations` a l'app, ou proceder a la main :")
        mode_emploi()


if __name__ == "__main__":
    sys.exit(main())
