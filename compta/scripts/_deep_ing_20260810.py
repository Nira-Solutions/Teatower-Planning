# -*- coding: utf-8 -*-
"""Investigation ciblee des encaissements clients ING non lettres (10/08/2026)."""
import os, re, json, xmlrpc.client
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = os.environ.get("ODOO_PWD")
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None): return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

# 1. communications structurees non resolues -> recherche globale account.move
STRUCTS = {
    19952: "000/0040/30348", 20026: "000/0040/27924", 20008: "000/0042/65471",
}
print("### COMM STRUCTUREES ###")
for bsl, s in STRUCTS.items():
    digits = re.sub(r"\D", "", s)
    res = call("account.move", "search_read",
               [["|", ["payment_reference", "like", s], ["payment_reference", "like", digits]]],
               {"fields": ["name", "partner_id", "amount_total", "amount_residual",
                           "payment_state", "invoice_date", "state"], "limit": 10})
    print(f"BSL {bsl} comm {s} -> {res}")

# 2. partenaires par nom pour les encaissements sans proposition
NEEDLES = {
    19466: "NANRETAIL", 19660: "ITM ALIMENTAIRE", 19630: "BALOISE",
    19784: "SMARTBOX", 20089: "SMARTBOX", 20065: "TOURNESOLS",
}
print("\n### PARTENAIRES / ENCOURS ###")
for bsl, needle in NEEDLES.items():
    ps = call("res.partner", "search_read", [[["name", "ilike", needle]]],
              {"fields": ["id", "name"], "limit": 15})
    print(f"\nBSL {bsl} '{needle}' -> {[(p['id'], p['name']) for p in ps]}")
    for p in ps:
        lines = call("account.move.line", "search_read",
                     [[["partner_id", "=", p["id"]], ["account_id", "=", 162],
                       ["reconciled", "=", False], ["parent_state", "=", "posted"],
                       ["amount_residual", "!=", 0]]],
                     {"fields": ["move_name", "amount_residual", "date", "id"], "limit": 40})
        for l in lines:
            print(f"    #{p['id']:6} {l['move_name']:22} {l['date']} res={l['amount_residual']:>9.2f} (line {l['id']})")

# 3. Carrefour : tout l'encours ouvert
print("\n### CARREFOUR encours 400000 ###")
cf = call("res.partner", "search_read", [[["name", "ilike", "carrefour"]]], {"fields": ["id", "name"], "limit": 40})
cfids = [p["id"] for p in cf]
lines = call("account.move.line", "search_read",
             [[["partner_id", "in", cfids], ["account_id", "=", 162], ["reconciled", "=", False],
               ["parent_state", "=", "posted"], ["amount_residual", "!=", 0]]],
             {"fields": ["move_name", "amount_residual", "date", "partner_id", "id"], "limit": 200, "order": "date"})
for l in lines:
    print(f"   {l['move_name']:22} {l['date']} res={l['amount_residual']:>10.2f} {l['partner_id'][1][:40]:40} line={l['id']}")
print("   TOTAL:", round(sum(l["amount_residual"] for l in lines), 2))

# 4. refs completes de quelques BSL a verifier
print("\n### REFS A VERIFIER ###")
for bid in [19610, 19703, 20247, 19992, 20008]:
    r = call("account.bank.statement.line", "read", [[bid]],
             {"fields": ["date", "amount", "payment_ref", "partner_id"]})[0]
    print(f"[{bid}] {r['date']} {r['amount']:.2f} :: {r['payment_ref']}")
