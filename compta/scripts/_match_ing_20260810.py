# -*- coding: utf-8 -*-
"""Proposition de matching automatique des lignes ING non lettrees (10/08/2026).

Lecture seule. Pour chaque BSL non lettree :
  - extrait le nom du payeur / beneficiaire du payment_ref
  - cherche les partenaires Odoo correspondants (fuzzy)
  - cherche une combinaison de factures ouvertes (400000 credit / 440000 debit)
    dont le total tombe sur le montant a +/- 5,00 EUR
"""
import os, re, json, itertools, unicodedata, xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

ACC_400000 = 162
ACC_440000 = 192
TOL = 5.00

def norm(s):
    if not s: return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9 ]", " ", s.upper())

bsls = json.load(open(os.path.join(os.path.dirname(__file__), "_scan_ing_20260810.json"), encoding="utf-8"))

# --- toutes les lignes ouvertes clients + fournisseurs ---
print("Chargement des lignes ouvertes 400000 / 440000 ...")
open_lines = call("account.move.line", "search_read",
                  [[["account_id", "in", [ACC_400000, ACC_440000]],
                    ["reconciled", "=", False],
                    ["parent_state", "=", "posted"],
                    ["amount_residual", "!=", 0]]],
                  {"fields": ["id", "account_id", "partner_id", "amount_residual", "move_id",
                              "move_name", "date", "name"], "limit": 20000})
print("  lignes ouvertes:", len(open_lines))

by_partner = {}
for l in open_lines:
    pid = (l.get("partner_id") or [0])[0]
    by_partner.setdefault((pid, (l["account_id"] or [0])[0]), []).append(l)

partners = call("res.partner", "search_read", [[]], {"fields": ["id", "name", "vat"], "limit": 60000})
pmap = {}
for p in partners:
    pmap.setdefault(norm(p["name"]), []).append(p["id"])
pnames = [(norm(p["name"]), p["id"], p["name"]) for p in partners if p["name"] and len(p["name"]) >= 4]

def guess_partners(text):
    t = norm(text)
    hits = []
    for n, pid, raw in pnames:
        if len(n) >= 5 and n in t:
            hits.append((len(n), pid, raw))
    hits.sort(reverse=True)
    seen, out = set(), []
    for _, pid, raw in hits:
        if pid in seen: continue
        seen.add(pid); out.append((pid, raw))
    return out[:6]

def find_combo(lines, target, tol=TOL, maxn=4):
    """cherche un sous-ensemble de residus dont la somme ~ target"""
    lines = sorted(lines, key=lambda l: -abs(l["amount_residual"]))[:14]
    best = None
    for n in range(1, min(maxn, len(lines)) + 1):
        for combo in itertools.combinations(lines, n):
            s = sum(c["amount_residual"] for c in combo)
            d = abs(s - target)
            if d <= tol and (best is None or d < best[0] or (d == best[0] and n < len(best[1]))):
                best = (d, combo)
        if best and best[0] <= 0.01:
            break
    return best

report = []
for b in bsls:
    amt = b["amount"]
    ref = b.get("payment_ref") or ""
    acc = ACC_400000 if amt > 0 else ACC_440000
    # cible signee : ligne client = debit(+) ; ligne fournisseur = credit(-)
    target = amt
    cands = guess_partners(ref)
    if b.get("partner_id"):
        cands = [(b["partner_id"][0], b["partner_id"][1])] + cands
    entry = {"bsl": b["id"], "date": b["date"], "amount": amt, "ref": ref[:160],
             "journal": b["journal_id"][1], "acc": acc, "props": []}
    for pid, pname in cands:
        lines = by_partner.get((pid, acc), [])
        if not lines: continue
        best = find_combo(lines, target)
        if best:
            d, combo = best
            entry["props"].append({
                "partner_id": pid, "partner": pname, "ecart": round(target - sum(c["amount_residual"] for c in combo), 2),
                "docs": [{"move": c["move_name"], "id": c["id"], "res": round(c["amount_residual"], 2), "date": c["date"]} for c in combo],
            })
        else:
            entry["props"].append({"partner_id": pid, "partner": pname, "ecart": None,
                                   "open": [{"move": c["move_name"], "res": round(c["amount_residual"], 2), "date": c["date"]} for c in lines[:8]]})
    report.append(entry)

with open(os.path.join(os.path.dirname(__file__), "_match_ing_20260810.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)

# affichage
for e in report:
    ok = [p for p in e["props"] if p.get("ecart") is not None]
    if not ok and not e["props"]:
        continue
    print("=" * 110)
    print(f"[{e['bsl']}] {e['date']} {e['amount']:>10.2f} {e['journal'][:20]:20} | {e['ref'][:80]}")
    for p in e["props"]:
        if p.get("ecart") is not None:
            docs = ", ".join(f"{d['move']}({d['res']:.2f})" for d in p["docs"])
            print(f"   >> {p['partner']} [#{p['partner_id']}] ecart={p['ecart']:+.2f} : {docs}")
        else:
            print(f"   -- {p['partner']} [#{p['partner_id']}] pas de combo ; ouvertes: "
                  + ", ".join(f"{d['move']}({d['res']:.2f})" for d in p.get("open", [])))
print("\n-> _match_ing_20260810.json")
