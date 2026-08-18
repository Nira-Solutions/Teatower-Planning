# -*- coding: utf-8 -*-
"""
Audit RFA Delhaize (commissions DSD/DSP 8 %) -- LECTURE SEULE.

Historique : Delhaize Le Lion S.A (partner 2912) percoit 8 % de commission sur les
livraisons directes (DSD) faites a ses magasins affilies. Teatower emet chaque mois
un avoir (out_refund) sur le partenaire 2912 :
    - ligne note   : "NC Teatower - Rebates MM/AAAA"
    - ligne produit: "Commissions DSP (8%x?)" -> compte 614200 RFA et publicite, TVA 6 %
Base retenue historiquement : CA HT du mois sur partner_id child_of 2912 (siege +
magasins "Affilie xxxxx"), net des avoirs de reprise/manquants du mois.

Usage : python _delhaize_rfa_audit.py
"""
import os
import collections
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
DELHAIZE = 2912
ACC_RFA = 869          # 614200 RFA et publicite
TAUX = 0.08

c = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common")
uid = c.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")
call = lambda mo, me, a, k=None: m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

# 1. avoirs de commission deja emis (lignes sur le compte RFA)
rfa = call("account.move.line", "search_read",
           [[["account_id", "=", ACC_RFA], ["partner_id", "=", DELHAIZE]]],
           {"fields": ["move_id", "name", "price_subtotal", "date"], "order": "date"})
deja = {l["move_id"][0] for l in rfa}
print("== avoirs de commission deja emis ==")
for l in rfa:
    print(f"  {l['date']}  {l['move_id'][1]:20s} {l['price_subtotal']:9.2f}")

# 2. CA mensuel du perimetre affilies, net des reprises (hors avoirs de commission)
mv = call("account.move", "search_read",
          [[["partner_id", "child_of", DELHAIZE],
            ["move_type", "in", ["out_invoice", "out_refund"]],
            ["state", "=", "posted"], ["invoice_date", ">=", "2025-01-01"]]],
          {"fields": ["id", "name", "move_type", "invoice_date", "amount_untaxed"], "limit": 5000})
brut = collections.defaultdict(float)
repr_ = collections.defaultdict(float)
for x in mv:
    k = x["invoice_date"][:7]
    if x["move_type"] == "out_invoice":
        brut[k] += x["amount_untaxed"]
    elif x["id"] not in deja:                 # on exclut les avoirs de commission eux-memes
        repr_[k] += x["amount_untaxed"]

print("\n== base RFA par mois (CA HT affilies, net des reprises) ==")
print(f"{'mois':9}{'brut HT':>11}{'reprises':>11}{'net HT':>11}{'8 %':>10}")
for k in sorted(brut):
    net = brut[k] - repr_[k]
    print(f"{k:9}{brut[k]:11.2f}{repr_[k]:11.2f}{net:11.2f}{net * TAUX:10.2f}")
