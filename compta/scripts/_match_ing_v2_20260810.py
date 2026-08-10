# -*- coding: utf-8 -*-
"""Matching v2 des lignes ING non lettrees (10/08/2026).

Strategies, par ordre de fiabilite :
  1. communication structuree BE (***000/0040/30348***) -> account.move.payment_reference
  2. numero de facture explicite dans la communication (INV/2026/xxxxx)
  3. IBAN du payeur -> res.partner.bank -> partenaire -> combinaison de factures ouvertes
  4. montant exact unique sur l'ensemble des lignes ouvertes 400000 / 440000
Lecture seule.
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

ACC_400000, ACC_440000 = 162, 192
TOL = 5.00
HERE = os.path.dirname(__file__)

bsls = json.load(open(os.path.join(HERE, "_scan_ing_20260810.json"), encoding="utf-8"))

open_lines = call("account.move.line", "search_read",
                  [[["account_id", "in", [ACC_400000, ACC_440000]],
                    ["reconciled", "=", False], ["parent_state", "=", "posted"],
                    ["amount_residual", "!=", 0]]],
                  {"fields": ["id", "account_id", "partner_id", "amount_residual",
                              "move_id", "move_name", "date"], "limit": 20000})

by_move = {}
by_partner = {}
for l in open_lines:
    by_move.setdefault((l["move_id"] or [0])[0], []).append(l)
    by_partner.setdefault(((l.get("partner_id") or [0])[0], (l["account_id"] or [0])[0]), []).append(l)

# --- index communication structuree ---
move_ids = list(by_move.keys())
moves = call("account.move", "read", [move_ids],
             {"fields": ["id", "name", "payment_reference", "ref", "partner_id",
                         "amount_total", "amount_residual", "move_type", "invoice_date"]})
def digits(s):
    return re.sub(r"\D", "", s or "")
struct_idx, name_idx = {}, {}
for mv in moves:
    name_idx[mv["name"]] = mv
    for f in ("payment_reference", "ref"):
        d = digits(mv.get(f))
        if len(d) == 12:
            struct_idx.setdefault(d, []).append(mv)

# --- index IBAN ---
banks = call("res.partner.bank", "search_read", [[]], {"fields": ["id", "acc_number", "partner_id"], "limit": 20000})
iban_idx = {}
for b in banks:
    k = re.sub(r"\s", "", (b.get("acc_number") or "")).upper()
    if k:
        iban_idx.setdefault(k, []).append((b["partner_id"] or [0])[0])

def find_combo(lines, target, tol=TOL, maxn=5):
    lines = sorted(lines, key=lambda l: -abs(l["amount_residual"]))[:16]
    best = None
    for n in range(1, min(maxn, len(lines)) + 1):
        for combo in itertools.combinations(lines, n):
            s = sum(c["amount_residual"] for c in combo)
            d = abs(s - target)
            if d <= tol and (best is None or d < best[0]):
                best = (d, combo)
        if best and best[0] <= 0.005:
            break
    return best

report = []
for b in bsls:
    amt = b["amount"]
    ref = b.get("payment_ref") or ""
    acc = ACC_400000 if amt > 0 else ACC_440000
    e = {"bsl": b["id"], "date": b["date"], "amount": round(amt, 2), "journal": b["journal_id"][1],
         "ref": ref, "acc": acc, "method": None, "partner": None, "partner_id": None,
         "docs": [], "ecart": None, "notes": []}

    # 1. communication structuree
    struct = re.findall(r"[*+]{3}(\d{3}/\d{4}/\d{5})[*+]{3}", ref)
    hit_moves = []
    for s in struct:
        hit_moves += struct_idx.get(digits(s), [])
    # 2. numero de facture explicite
    for nm in re.findall(r"(INV/\d{4}/\d{4,6})", ref):
        if nm in name_idx:
            hit_moves.append(name_idx[nm])
    if hit_moves:
        seen = set(); mv_list = []
        for mv in hit_moves:
            if mv["id"] in seen: continue
            seen.add(mv["id"]); mv_list.append(mv)
        lines = [l for mv in mv_list for l in by_move.get(mv["id"], []) if (l["account_id"] or [0])[0] == acc]
        if lines:
            tot = sum(l["amount_residual"] for l in lines)
            e.update(method="STRUCT/REF", partner=(mv_list[0].get("partner_id") or [0, "?"])[1],
                     partner_id=(mv_list[0].get("partner_id") or [0])[0],
                     docs=[{"move": l["move_name"], "line": l["id"], "res": round(l["amount_residual"], 2)} for l in lines],
                     ecart=round(amt - tot, 2))
            report.append(e); continue
        e["notes"].append(f"comm structuree {struct} trouvee mais plus de ligne {acc} ouverte")

    # 3. IBAN payeur
    ibans = re.findall(r"\b([A-Z]{2}\d{2}[A-Z0-9]{8,26})\b", ref.replace(" ", ""))
    ibans += [re.sub(r"\s", "", x) for x in re.findall(r"IBAN:\s*([A-Z]{2}[\d ]{10,30})", ref)]
    pids = []
    for ib in set(ibans):
        pids += iban_idx.get(ib.upper(), [])
    if b.get("partner_id"):
        pids.append(b["partner_id"][0])
    best_p = None
    for pid in dict.fromkeys(pids):
        lines = by_partner.get((pid, acc), [])
        if not lines: continue
        c = find_combo(lines, amt)
        if c and (best_p is None or c[0] < best_p[0]):
            best_p = (c[0], c[1], pid)
    if best_p:
        d, combo, pid = best_p
        pname = call("res.partner", "read", [[pid]], {"fields": ["name"]})[0]["name"]
        e.update(method="IBAN", partner=pname, partner_id=pid,
                 docs=[{"move": l["move_name"], "line": l["id"], "res": round(l["amount_residual"], 2)} for l in combo],
                 ecart=round(amt - sum(l["amount_residual"] for l in combo), 2))
        report.append(e); continue
    if pids:
        e["notes"].append(f"partenaire(s) identifie(s) par IBAN {list(dict.fromkeys(pids))} mais aucune combinaison a +/-5 EUR")

    # 4. montant exact unique
    exact = [l for l in open_lines if (l["account_id"] or [0])[0] == acc and abs(l["amount_residual"] - amt) <= 0.01]
    if len(exact) == 1:
        l = exact[0]
        e.update(method="MONTANT_EXACT_UNIQUE", partner=(l.get("partner_id") or [0, "?"])[1],
                 partner_id=(l.get("partner_id") or [0])[0],
                 docs=[{"move": l["move_name"], "line": l["id"], "res": round(l["amount_residual"], 2)}],
                 ecart=round(amt - l["amount_residual"], 2))
    elif len(exact) > 1:
        e["notes"].append("montant exact ambigu: " + ", ".join(
            f"{l['move_name']}/{(l.get('partner_id') or [0,'?'])[1]}" for l in exact[:6]))
    report.append(e)

json.dump(report, open(os.path.join(HERE, "_match_ing_v2_20260810.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

matched = [e for e in report if e["method"]]
print(f"BSL non lettrees: {len(report)} | proposition trouvee: {len(matched)}\n")
for e in sorted(matched, key=lambda x: x["date"]):
    docs = ", ".join(f"{d['move']}({d['res']:.2f})" for d in e["docs"])
    print(f"[{e['bsl']}] {e['date']} {e['amount']:>10.2f} {e['method']:22} ecart={e['ecart']:+7.2f} "
          f"| {str(e['partner'])[:34]:34} | {docs[:90]}")
print("\n--- SANS PROPOSITION ---")
for e in sorted([x for x in report if not x["method"]], key=lambda x: x["date"]):
    print(f"[{e['bsl']}] {e['date']} {e['amount']:>10.2f} | {e['ref'][:95]}")
    for n in e["notes"]:
        print(f"      ! {n[:150]}")
