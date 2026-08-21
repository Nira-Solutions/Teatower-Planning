# -*- coding: utf-8 -*-
"""Subset-sum EXHAUSTIF (DP en centimes) sur les 71 factures Carrefour ouvertes.

Objectif : verifier s'il existe un sous-ensemble exact (n'importe quelle taille) pour
4.862,06 et 1.396,75, et surtout COMBIEN il y en a. Un nombre astronomique de solutions
= aucune information -> il faut basculer en FIFO.
"""
import os
from collections import defaultdict
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None): return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

CRF = 6596
inv = call("account.move", "search_read",
           [[["partner_id", "child_of", CRF], ["state", "=", "posted"],
             ["payment_state", "in", ["not_paid", "partial"]],
             ["move_type", "in", ["out_invoice", "out_refund"]]]],
           {"fields": ["name", "invoice_date", "amount_residual"], "order": "invoice_date asc"})
items = [(i["name"], int(round(i["amount_residual"] * 100)), i["invoice_date"]) for i in inv]
print(f"{len(items)} factures ouvertes, total {sum(x[1] for x in items)/100:,.2f}")

CAP = 10_000_000  # on plafonne le nombre de solutions comptees


def count_subsets(items, target):
    """DP : nb de sous-ensembles atteignant chaque somme (plafonne)."""
    ways = defaultdict(int)
    ways[0] = 1
    for _, v, _ in items:
        if v <= 0:
            continue
        for s in sorted([s for s in ways if s + v <= target], reverse=True):
            ways[s + v] = min(ways[s + v] + ways[s], CAP)
    return ways.get(target, 0)


def one_solution(items, target):
    """Reconstruit UNE solution si elle existe."""
    reach = {0: None}
    for idx, (_, v, _) in enumerate(items):
        if v <= 0:
            continue
        for s in sorted([s for s in reach if s + v <= target], reverse=True):
            if s + v not in reach:
                reach[s + v] = (s, idx)
    if target not in reach:
        return None
    out, cur = [], target
    while cur:
        prev, idx = reach[cur]
        out.append(items[idx])
        cur = prev
    return out[::-1]


for target_eur in (4862.06, 1396.75):
    t = int(round(target_eur * 100))
    n = count_subsets(items, t)
    print(f"\n=== cible {target_eur:,.2f} -> {n:,} sous-ensemble(s) exact(s)"
          + ("  [PLAFONNE]" if n >= CAP else ""))
    if 0 < n <= 3:
        sol = one_solution(items, t)
        for nm, v, d in sol:
            print(f"    {nm:<20} {d} {v/100:>10,.2f}")
