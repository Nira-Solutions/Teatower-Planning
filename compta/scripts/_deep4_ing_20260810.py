# -*- coding: utf-8 -*-
"""Traitement historique des titres-repas (Pluxee/Edenred/Monizze), Baloise, iPiD
+ subset-sum DP pour Carrefour / Kirchner + refs completes 19466 / 19660."""
import os, re, xmlrpc.client
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = os.environ.get("ODOO_PWD")
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None): return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

print("### HISTORIQUE : comment les lignes PLUXEE/EDENRED/MONIZZE deja lettrees ont-elles ete imputees ? ###")
for needle in ["PLUXEE", "EDENRED", "MONIZZE", "BALOISE", "SMARTBOX"]:
    bs = call("account.bank.statement.line", "search_read",
              [[["payment_ref", "ilike", needle], ["is_reconciled", "=", True]]],
              {"fields": ["id", "date", "amount", "move_id"], "order": "date desc", "limit": 4})
    print(f"\n-- {needle} : {len(bs)} lignes lettrees recentes")
    for b in bs:
        lines = call("account.move.line", "search_read", [[["move_id", "=", b["move_id"][0]]]],
                     {"fields": ["account_id", "debit", "credit", "partner_id", "name"]})
        print(f"   [{b['id']}] {b['date']} {b['amount']:.2f}")
        for l in lines:
            print(f"       {str(l['account_id'][1])[:44]:44} d={l['debit']:>9.2f} c={l['credit']:>9.2f} "
                  f"{str((l.get('partner_id') or [0,'-'])[1])[:24]}")

print("\n### REFS COMPLETES ###")
for bid in [19466, 19660, 19630]:
    r = call("account.bank.statement.line", "read", [[bid]], {"fields": ["date", "amount", "payment_ref"]})[0]
    print(f"[{bid}] {r['date']} {r['amount']:.2f} :: {r['payment_ref']}")


def subset_sum(lines, target_cents, tol=0):
    """DP exacte sur les centimes (valeurs absolues), retourne une solution."""
    vals = [(l, abs(round(l["amount_residual"] * 100))) for l in lines]
    reach = {0: []}
    for l, v in vals:
        new = {}
        for s, path in reach.items():
            ns = s + v
            if ns <= target_cents + tol and ns not in reach:
                new[ns] = path + [l]
        reach.update(new)
    for d in range(0, tol + 1):
        for cand in (target_cents - d, target_cents + d):
            if cand in reach and reach[cand]:
                return d, reach[cand]
    return None


print("\n### CARREFOUR subset-sum exact 4862.06 (DP) ###")
cf = call("res.partner", "search_read", [[["name", "ilike", "carrefour"]]], {"fields": ["id"], "limit": 40})
cl = call("account.move.line", "search_read",
          [[["partner_id", "in", [p["id"] for p in cf]], ["account_id", "=", 162], ["reconciled", "=", False],
            ["parent_state", "=", "posted"], ["amount_residual", ">", 0]]],
          {"fields": ["move_name", "amount_residual", "date", "id"], "limit": 200, "order": "date"})
r = subset_sum(cl, 486206, tol=500)
print("  ", "AUCUNE" if not r else (f"ecart {r[0]}c : " + ", ".join(f"{x['move_name']}({x['amount_residual']:.2f})" for x in r[1])))

print("\n### KIRCHNER subset-sum 12837.54 (DP) ###")
kl = call("account.move.line", "search_read",
          [[["partner_id", "=", 7195], ["account_id", "=", 192], ["reconciled", "=", False],
            ["parent_state", "=", "posted"], ["amount_residual", "<", 0]]],
          {"fields": ["move_name", "amount_residual", "date", "id"], "limit": 200, "order": "date"})
r = subset_sum(kl, 1283754, tol=500)
print("  ", "AUCUNE" if not r else (f"ecart {r[0]}c : " + ", ".join(f"{x['move_name']}({x['amount_residual']:.2f})" for x in r[1])))
