"""
Retour aux prix pleins Shopify apres la promo -30% "Escale a Cassis" du 27/07/2026.

  I0866 (20 infusettes) : 7,70 -> 11,00 EUR TTC, prix barre retire
  V0866 (100 g vrac)    : 7,00 -> 10,00 EUR TTC, prix barre retire

Cote Odoo POS il n'y a RIEN a faire : le programme loyalty #50 a
date_from = date_to = 2026-07-27, il s'eteint tout seul le 28/07.

Usage :
    "C:\\Program Files\\LibreOffice\\program\\python.exe" scripts/promo_revert_escale_cassis.py
    ... ou avec un python systeme si reinstalle.
Ajouter "dry" en argument pour ne rien ecrire.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_client import shopify

DRY = len(sys.argv) > 1 and sys.argv[1].lower().startswith("dry")

# variant_id -> (sku, prix plein TTC a restaurer)
TARGETS = {
    48728854954323: ("I0866", "11.00"),
    48743857684819: ("V0866", "10.00"),
}

print(f"MODE: {'DRY-RUN' if DRY else 'APPLY'}\n")

for vid, (sku, full) in TARGETS.items():
    cur = shopify.get(f"variants/{vid}.json")["variant"]
    print(f"{sku} (variant {vid}) avant : price={cur['price']} compare_at={cur['compare_at_price']}")
    if cur["price"] == full and not cur["compare_at_price"]:
        print("  -> deja au prix plein, rien a faire")
        continue
    if DRY:
        print(f"  [DRY-RUN] remettrait price={full}, compare_at=None")
        continue
    upd = shopify.put(
        f"variants/{vid}.json",
        json_body={"variant": {"id": vid, "price": full, "compare_at_price": None}},
    )["variant"]
    print(f"  -> apres : price={upd['price']} compare_at={upd['compare_at_price']}")

print("\nTermine.")
