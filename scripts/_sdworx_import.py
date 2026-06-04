# -*- coding: utf-8 -*-
"""Import des ecritures de paie SD Worx (1BT1014.xlsx) — oct 2025 -> mai 2026.
Replique la structure de MISC/25-26/09/0002 (comptable) :
- garde 62x (charges), 7xxx (produits), 4550/5790 (dettes), 453x/454x cote CREDIT
- exclut le bloc facture SD Worx (6132, 4110, 4400, 7440) deja en factures fournisseur
- exclut les transferts 453x/454x cote DEBIT (zeroes vers 4400 chez SD)
Usage: python _sdworx_import.py [--apply]
"""
import openpyxl, sys, xmlrpc.client
from collections import defaultdict
sys.stdout.reconfigure(encoding="utf-8")
import warnings; warnings.filterwarnings("ignore")

APPLY = "--apply" in sys.argv
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})

MAP = {
  "4530":"453000","4540":"454000","4541":"454000","4550":"455000","4560":"456000",
  "4909":"456000",  # provision compl. cotisations sociales -> meme rubrique dettes sociales (a defaut)
  "5790":"579000",
  "62020":"620200","62022":"620202","62030":"620300","62051":"620510","62056":"620560","62057":"620560",
  "62060":"743100","62061":"743100",   # deduction ATN -> produit (convention comptable sept)
  "62120":"621200","62130":"621300","6219":"621200",
  "62320":"623000","62322":"623220","62332":"623220","62390":"623901",
  "62501":"625000","62502":"625000",
  "7430":"743001","7432":"743901","7439":"743901","7440":None,
  "6132":None,"4110":None,"4400":None,   # bloc facture SD Worx -> exclu
}
EXCL_DEBIT_ONLY = {"4530","4540","4541"}   # cote D = transfert vers 4400 -> exclu

wb = openpyxl.load_workbook(r"C:\Users\FlowUP\OneDrive\Teatower\1BT1014.xlsx", data_only=True)
ws = wb["Sheet1"]
data = defaultdict(list)
for r in ws.iter_rows(min_row=2, values_only=True):
    if not r[3]: continue
    compte, dc, desc, amt, p_du = str(r[3]), r[4], r[5], float(r[6]), str(r[8])[:7]
    data[p_du].append((compte, dc, desc, amt))

# comptes Odoo
acc_cache = {}
def acc_id(code):
    if code not in acc_cache:
        found = call("account.account","search",[[["code","=",code]]])
        acc_cache[code] = found[0] if found else None
    return acc_cache[code]

# verifier que tous les comptes cibles existent
needed = sorted(set(v for v in MAP.values() if v))
missing = [c for c in needed if not acc_id(c)]
print("Comptes cibles manquants dans Odoo:", missing or "aucun")
if "456000" in missing:
    nid = call("account.account","create",[{"code":"456000","name":"Pécule de vacances à payer","account_type":"liability_current","reconcile":False}])
    acc_cache["456000"] = nid
    print("  -> 456000 'Pécule de vacances à payer' cree")

def build_month(period):
    lines = defaultdict(lambda: [0.0, ""])  # (odoo_code) -> [solde D-C, desc]
    skipped = defaultdict(float)
    for compte, dc, desc, amt in data[period]:
        target = MAP.get(compte, "??")
        if target == "??":
            print(f"  !! code SD inconnu {compte} {desc} {amt}"); continue
        if target is None or (compte in EXCL_DEBIT_ONLY and dc == "D"):
            skipped[compte] += amt if dc=="D" else -amt
            continue
        key = (target, desc[:60] if desc else target)
        lines[key][0] += amt if dc == "D" else -amt
        lines[key][1] = desc or ""
    bal = sum(v[0] for v in lines.values())
    return lines, skipped, bal

# ---- validation sur septembre 2025 ----
print("\n=== VALIDATION 2025-09 (vs MISC/25-26/09/0002) ===")
lines, skipped, bal = build_month("2025-09")
for (code, desc), (amt, _) in sorted(lines.items()):
    if abs(amt) < 0.005: continue
    print(f"  {code} {'D' if amt>0 else 'C'} {abs(amt):>10.2f}  {desc[:45]}")
print(f"  EQUILIBRE: {bal:+.4f}")

# ---- les 8 mois manquants ----
MONTHS = ["2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05"]
total_charge = 0.0
created = []
for m in MONTHS:
    lines, skipped, bal = build_month(m)
    charge = sum(v[0] for (c,_), v in lines.items() if c.startswith("62"))
    produits = -sum(v[0] for (c,_), v in lines.items() if c.startswith("74"))
    total_charge += charge - produits
    print(f"\n=== {m} : charges 62x {charge:,.2f} | produits 74x {produits:,.2f} | equilibre {bal:+.4f} ===")
    if abs(bal) > 0.02:
        print("  !! DESEQUILIBRE — mois non comptabilise"); continue
    if not APPLY: continue
    # construire l'OD
    mvlines = []
    for (code, desc), (amt, _) in sorted(lines.items()):
        amt = round(amt, 2)
        if abs(amt) < 0.005: continue
        mvlines.append((0,0,{"account_id":acc_id(code),
                             "debit": amt if amt>0 else 0.0,
                             "credit": -amt if amt<0 else 0.0,
                             "name": f"{desc[:55]} — paie {m}"}))
    # ajustement arrondi eventuel
    d = round(sum(l[2]["debit"] for l in mvlines) - sum(l[2]["credit"] for l in mvlines), 2)
    if abs(d) >= 0.01:
        mvlines.append((0,0,{"account_id":acc_id("657100" if d<0 else "757100"),
                             "debit": -d if d<0 else 0.0, "credit": d if d>0 else 0.0,
                             "name": f"Arrondi import paie {m}"}))
    misc = call("account.journal","search",[[["type","=","general"]]],{"limit":1})[0]
    y, mo = m.split("-")
    import calendar
    last = calendar.monthrange(int(y), int(mo))[1]
    mid = call("account.move","create",[{
        "move_type":"entry","journal_id":misc,"date":f"{m}-{last}",
        "ref":f"Paie SD Worx {mo}/{y} — import 1BT1014 (validé Nicolas 04/06/2026)",
        "line_ids":mvlines}])
    call("account.move","action_post",[[mid]])
    name = call("account.move","read",[[mid]],{"fields":["name"]})[0]["name"]
    created.append((m, name, charge - produits))
    print(f"  -> OD {name} postee ({len(mvlines)} lignes)")

print(f"\nMODE: {'APPLY' if APPLY else 'DRY-RUN'} | charge nette totale 8 mois: {total_charge:,.2f} EUR")
for m, n, c in created: print(f"  {m}: {n} ({c:,.2f})")
