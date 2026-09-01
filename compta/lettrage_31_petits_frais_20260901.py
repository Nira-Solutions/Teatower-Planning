# -*- coding: utf-8 -*-
"""
Suite du lettrage ING/Belfius du 01/09/2026 : imputation des petites lignes
carte / Bancontact qui ne peuvent pas se lettrer contre une piece (aucune
facture d achat enregistree). Chaque imputation suit un precedent identique
deja present dans le journal.

    python lettrage_31_petits_frais_20260901.py         -> DRY-RUN
    python lettrage_31_petits_frais_20260901.py apply    -> execution
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


ACC_600 = 234   # 600000 Purchases of Raw Materials
ACC_611129 = 827   # 611129 Licences informatiques
ACC_612 = 838   # 612000 Fournitures
ACC_613099 = 854   # 613099 Frais divers
ACC_615230 = 872   # 615230 Decoration / fleurs
ACC_616600 = 879   # 616600 Frais de marketing
ACC_440 = 192   # 440000 Suppliers
ACC_650 = 281   # 650000 Interest, Commission and Other Charges

P_FAIRE = 6404
P_BRICO = 7416

LIGNES = [
    # (bsl, montant, compte, partenaire, justification)
    (19853, -342.77, ACC_600, P_FAIRE, "Achat Faire (MIAMIO) -- precedent BSL 19854/19855/19426/19428"),
    (19857, -180.51, ACC_600, P_FAIRE, "Achat Faire (NCA Europe Design) -- meme precedent"),
    (20401, -272.04, ACC_600, P_FAIRE, "Achat Faire (Ogo Living) -- meme precedent"),
    (19999,  -50.00, ACC_616600, None, "Meta Ads (Facebook Payments) -- publicite"),
    (20123,  -50.00, ACC_616600, None, "Meta Ads (Facebook Payments) -- publicite"),
    (20111,  -50.00, ACC_616600, None, "Braderie de Waterloo -- emplacement/evenement boutique"),
    (20591,  -22.40, ACC_616600, None, "RJ Pasta Bar Arlon -- precedent BSL 19213 (52,90 -> 616600)"),
    (20079,  -21.98, ACC_611129, None, "Google Play (abonnement) -- licences informatiques"),
    (20126,  -11.72, ACC_615230, None, "Carrefour Express Liege -- precedent BSL 11627/11629 (615230)"),
    (20374,  -22.10, ACC_615230, None, "Le Fleuron Tournai (fleuriste) -- decoration boutique"),
    (20125,  -11.47, ACC_613099, None, "Familia Hannut -- petit achat divers"),
    (20616, -247.50, ACC_613099, None, "Compte Citoyen -- precedent BSL 16971/15497 (613099)"),
    (20213,  -43.10, ACC_612, None, "sr-Get your mug Liege -- fournitures boutique"),
    (20345,   -9.60, ACC_612, None, "sr-Get your mug Liege -- fournitures boutique"),
    (20615, -195.00, ACC_440, P_BRICO, "Brico Waterloo -- precedent BSL 17182/15916 (440000 + Brico)"),
    (19640,   -0.01, ACC_650, None, "Mollie -- virement de verification de compte"),
    (19641,   -0.01, ACC_650, None, "Mollie -- virement de verification de compte"),
]

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 92)

total = 0.0
for bsl, montant, acc, partner, note in LIGNES:
    b = call("account.bank.statement.line", "read", [[bsl]], {"fields": ["move_id", "date"]})[0]
    ls = call("account.move.line", "search_read", [[["move_id", "=", b["move_id"][0]]]],
              {"fields": ["id", "account_id"]})
    s = [l for l in ls if l["account_id"][1].startswith("499")]
    if not s:
        print("  BSL %-6d [SKIP] deja traitee -- %s" % (bsl, note))
        continue
    total += montant
    print("  BSL %-6d %s %9.2f -> %-5d %-8s | %s" % (
        bsl, b["date"], montant, acc, ("p%d" % partner) if partner else "", note))
    if not APPLY:
        continue
    vals = {"account_id": acc}
    if partner:
        vals["partner_id"] = partner
    call("account.move.line", "write", [[s[0]["id"]], vals])
    print("        [OK] repointee")

print("\nTotal impute : %.2f EUR" % total)
rest = call("account.bank.statement.line", "search_count",
            [[["journal_id", "in", [14, 36]], ["is_reconciled", "=", False]]])
print("Lignes ING+Belfius encore non lettrees : %d" % rest)
