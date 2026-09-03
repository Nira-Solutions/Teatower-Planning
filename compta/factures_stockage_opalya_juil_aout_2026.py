# -*- coding: utf-8 -*-
"""
Rattrapage de la facturation stockage Opalya / Terracotta Beauty SRL (#123541).

Facture mensuelle du service de stockage (19 palettes x 10 EUR + 25 EUR de forfait
gestion = 215 EUR HT / 260,15 EUR TTC). Facture jusqu'en juin 2026 puis oublie :
  INV/2026/02422  30/04  Avril    posted  impayee
  INV/2026/02989  10/06  Mai      posted  impayee
  INV/2026/03315  30/06  Juin     posted  payee
  -> JUILLET et AOUT 2026 manquants.

Aucune recurrence automatique n'existe dans Odoo (auto_post='no' sur les 3
factures) : la mention "recurrence INV/2026/02989" est du texte libre. Rien ne
s'est casse, la facturation est manuelle et a simplement ete oubliee.

Comptage des palettes verifie sur les quants au 03/09/2026 : 19 emplacements
TT/Stock/PICK occupes -- OPA001 10, OPA002 5, OPA003 4. Inchange depuis avril
(la seule sortie, TT/OUT/08777 du 07/07, porte 23 unites et ne libere pas de
palette). Le nombre facture reste donc 19 pour juillet et pour aout.

Verrous comptables : sale_lock_date / tax_lock_date = 2025-06-30, TVA
trimestrielle -> Q3 2026 encore ouvert, les dates 31/07 et 31/08 sont valides.

    python factures_stockage_opalya_juil_aout_2026.py         -> DRY-RUN
    python factures_stockage_opalya_juil_aout_2026.py apply   -> creation + post
"""
import os
import sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
UID = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return _m.execute_kw(DB, UID, PWD, model, method, args, kw or {})


PARTNER = 123541          # Terracotta Beauty SRL
JOURNAL = 9               # Customer Invoices (INV)
FP_B2B = 1                # Belgium B2B
BANK = 3979               # BE30 3631 6408 2311 - ING
PROD_STOCK = 7751         # [OPA-STOCK] Stockage palette standard - mensuel
PROD_GESTION = 7752       # [OPA-GESTION] Forfait gestion Odoo mensuel - Opalya
ACC_700 = 320             # 700000 -- compte utilise sur les 3 factures precedentes
TAX_21 = 3                # taxe telle qu'appliquee par la FP Belgium B2B
PALETTES = 19

MOIS = [
    dict(libelle="Juillet 2026", debut="01/07/2026", fin="31/07/2026",
         date="2026-07-31", due="2026-08-30"),
    dict(libelle="Aout 2026", debut="01/08/2026", fin="31/08/2026",
         date="2026-08-31", due="2026-09-30"),
]

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 92)

# garde-fou : ne pas creer un doublon si la periode est deja facturee
existantes = call("account.move", "search_read",
                  [[["partner_id", "child_of", [PARTNER]],
                    ["move_type", "=", "out_invoice"],
                    ["invoice_date", ">=", "2026-07-01"]]],
                  {"fields": ["name", "invoice_date", "ref", "amount_total", "state"]})
print("Factures deja presentes a partir du 01/07/2026 : %s" % (existantes or "AUCUNE"))

for m in MOIS:
    deja = [x for x in existantes if (x.get("ref") or "").lower().startswith(
        "stockage " + m["libelle"].split()[0].lower())]
    print("\n--- %s ---" % m["libelle"])
    if deja:
        print("  [SKIP] deja facture : %s" % deja)
        continue

    narration = (
        "<p>Prestations stockage et gestion - %s (du %s au %s)\n\n"
        "Contrat : Convention de stockage Teatower / Terracotta Beauty (Opalya).\n"
        "Lieu de stockage : entrepot Teatower, Baillonville.</p>"
        % (m["libelle"], m["debut"], m["fin"]))
    lignes = [
        (0, 0, {"product_id": PROD_STOCK,
                "name": "Stockage palette standard (≤ 1,2 × 0,8 m, ≤ 800 kg) "
                        "— %s\n3 SKU Opalya stockés : OPA001 (10 palettes) + "
                        "OPA002 (5) + OPA003 (4)" % m["libelle"],
                "quantity": PALETTES, "price_unit": 10.0,
                "account_id": ACC_700, "tax_ids": [(6, 0, [TAX_21])]}),
        (0, 0, {"product_id": PROD_GESTION,
                "name": "Forfait gestion Odoo mensuel — suivi stocks, rapports, "
                        "facturation — %s" % m["libelle"],
                "quantity": 1.0, "price_unit": 25.0,
                "account_id": ACC_700, "tax_ids": [(6, 0, [TAX_21])]}),
    ]
    vals = {
        "move_type": "out_invoice",
        "partner_id": PARTNER,
        "journal_id": JOURNAL,
        "invoice_date": m["date"],
        "invoice_date_due": m["due"],
        "fiscal_position_id": FP_B2B,
        "partner_bank_id": BANK,
        "ref": "Stockage %s" % m["libelle"],
        "narration": narration,
        "invoice_line_ids": lignes,
    }
    print("  date %s  echeance %s  ref='%s'" % (m["date"], m["due"], vals["ref"]))
    print("  %d palettes x 10,00 = %.2f  +  forfait gestion 25,00  =  %.2f HT"
          % (PALETTES, PALETTES * 10.0, PALETTES * 10.0 + 25.0))
    if not APPLY:
        continue
    mid = call("account.move", "create", [vals])
    call("account.move", "action_post", [[mid]])
    r = call("account.move", "read", [[mid]],
             {"fields": ["name", "invoice_date", "amount_untaxed", "amount_total",
                         "amount_residual", "state"]})[0]
    print("  [OK] %s  HT %.2f  TTC %.2f  residuel %.2f  (%s)"
          % (r["name"], r["amount_untaxed"], r["amount_total"],
             r["amount_residual"], r["state"]))

print("\n" + "=" * 92)
solde = call("account.move", "search_read",
             [[["partner_id", "child_of", [PARTNER]],
               ["move_type", "=", "out_invoice"], ["state", "=", "posted"],
               ["payment_state", "!=", "paid"]]],
             {"fields": ["name", "invoice_date", "invoice_date_due", "amount_residual"],
              "order": "invoice_date asc"})
tot = 0.0
print("ENCOURS CLIENT Terracotta Beauty :")
for x in solde:
    tot += x["amount_residual"]
    print("  %-16s %s  ech %s  %8.2f" % (x["name"], x["invoice_date"],
                                         x["invoice_date_due"], x["amount_residual"]))
print("  %-16s %38s %8.2f" % ("TOTAL", "", tot))
