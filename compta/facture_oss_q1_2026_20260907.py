# -*- coding: utf-8 -*-
"""
Facture fournisseur pour la TVA OSS Q1.2026 reclamee par la DGFiP (365,43 EUR),
a payer le vendredi 11/09/2026.

POURQUOI LA LIGNE VA SUR 451001 ET NON SUR UN COMPTE DE CHARGE :
la TVA OSS a deja ete comptabilisee en dette au moment de chaque vente
(credit 451001, facture par facture). Passer cette piece en charge la
compterait une seconde fois. La facture ne fait donc que DEPLACER la dette :
  D 451001 « TVA a payer OSS »   365,43
  C 440000 fournisseur DGFiP     365,43
Zero impact resultat. Ce qu'elle apporte : la dette devient un fournisseur
identifie, avec une echeance, et l'echeancier la reprend tout seul.

Le solde Q1.2026 restant sur 451001 apres cette piece sera de 72,73 EUR
(438,16 declares - 365,43 reclames par la France) : c'est la part de
l'Allemagne, du Luxembourg et des Pays-Bas, qui reclameront chacun sur leur
propre compte. Elle reste en ligne manuelle dans l'echeancier tant qu'aucun
rappel n'est arrive.

    python facture_oss_q1_2026_20260907.py        -> DRY-RUN
    python facture_oss_q1_2026_20260907.py apply   -> execution
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


ACC_451001 = 934          # TVA a payer OSS
JRN_ACHATS = 10           # Vendor Bills
MONTANT = 365.43
REF = "BE/BE0656763145/Q1.2026"
DATE = "2026-09-07"
ECHEANCE = "2026-09-11"   # vendredi
NOM_PARTNER = "DGFiP — Pôle national TVA du commerce en ligne"

NARRATION = (
    "<p>Rappel de la Direction générale des Finances publiques (France) reçu le "
    "07/09/2026 : la déclaration OSS <b>BE/BE0656763145/Q1.2026</b>, déposée le "
    "01/05/2026, n'a jamais été payée. Le délai de paiement via l'administration "
    "belge étant dépassé, la part française se règle directement à la DGFiP.</p>"
    "<p><b>Coordonnées annoncées dans le rappel</b> — titulaire « POLE NATIONAL "
    "TVA DU COMMERCE EN LIGNE », IBAN FR19 3000 1003 0949 78E0 5003 016, BIC "
    "BDFEFRPPCCT (Banque de France). Checksum IBAN valide et code banque 30001 = "
    "Banque de France. <b>À recouper avec le portail OSS / impots.gouv.fr avant "
    "de virer</b> : un checksum ne prouve pas à qui appartient le compte.</p>"
    "<p><b>Attention, la France n'est pas seule créancière.</b> Le trimestre "
    "Q1.2026 vaut 438,16 € au compte 451001 : FR 364,36 + DE 8,34 + LU 25,23 + "
    "NL 40,23. Payer les 365,43 € ne solde pas le trimestre — il restera 72,73 € "
    "sur 451001 pour l'Allemagne, le Luxembourg et les Pays-Bas, qui réclameront "
    "sur leurs propres comptes.</p>"
    "<p>Aucun impact résultat : la ligne est imputée sur 451001, la TVA ayant "
    "déjà été mise en dette vente par vente.</p>"
)

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 90)

# --- garde-fou : la piece existe-t-elle deja ? ---------------------------
deja = call("account.move", "search_read",
            [[["ref", "=", REF], ["move_type", "=", "in_invoice"]]],
            {"fields": ["name", "amount_total", "state", "payment_state"]})
if deja:
    print("\n[SKIP] la facture existe deja :", deja)
    sys.exit(0)

# --- partenaire ----------------------------------------------------------
p = call("res.partner", "search_read", [[["name", "=", NOM_PARTNER]]], {"fields": ["id"]})
if p:
    pid = p[0]["id"]
    print("\n  partenaire existant #%d" % pid)
else:
    fr = call("res.country", "search", [[["code", "=", "FR"]]])[0]
    print("\n  partenaire A CREER : %s (France)" % NOM_PARTNER)
    pid = None
    if APPLY:
        pid = call("res.partner", "create", [{
            "name": NOM_PARTNER,
            "company_type": "company",
            "country_id": fr,
            "city": "Noisy-le-Grand",
            "supplier_rank": 1,
            "comment": "Service de la DGFiP qui recouvre la TVA OSS due à la "
                       "France quand le délai de paiement via l'État membre "
                       "d'identification (Belgique) est dépassé.",
        }])
        print("  [OK] partenaire cree #%d" % pid)

# --- la facture ----------------------------------------------------------
print("\n  FACTURE : %s  %.2f EUR  date %s  echeance %s" % (REF, MONTANT, DATE, ECHEANCE))
print("            journal %d (Vendor Bills), ligne sur 451001 (id %d), SANS taxe"
      % (JRN_ACHATS, ACC_451001))
print("            -> D 451001 %.2f / C 440000 %.2f : aucun impact resultat"
      % (MONTANT, MONTANT))

if not APPLY:
    print("\n  (dry-run : relancer avec 'apply')")
    sys.exit(0)

mid = call("account.move", "create", [{
    "move_type": "in_invoice",
    "partner_id": pid,
    "journal_id": JRN_ACHATS,
    "invoice_date": DATE,
    "date": DATE,
    "invoice_date_due": ECHEANCE,
    "ref": REF,
    "payment_reference": REF,
    "narration": NARRATION,
    "invoice_line_ids": [(0, 0, {
        "name": "TVA OSS Q1.2026 — part France (déclaration du 01/05/2026)",
        "account_id": ACC_451001,
        "quantity": 1.0,
        "price_unit": MONTANT,
        "tax_ids": [(6, 0, [])],
    })],
}])
call("account.move", "action_post", [[mid]])
mv = call("account.move", "read", [[mid]],
          {"fields": ["name", "amount_total", "amount_residual", "state",
                      "payment_state", "invoice_date_due"]})[0]
print("\n  [OK] %s  %.2f EUR  residuel %.2f  echeance %s  %s/%s"
      % (mv["name"], mv["amount_total"], mv["amount_residual"],
         mv["invoice_date_due"], mv["state"], mv["payment_state"]))

lignes = call("account.move.line", "search_read", [[["move_id", "=", mid]]],
              {"fields": ["account_id", "debit", "credit"]})
for l in lignes:
    print("       %-40s D=%8.2f C=%8.2f" % (l["account_id"][1][:40], l["debit"], l["credit"]))
