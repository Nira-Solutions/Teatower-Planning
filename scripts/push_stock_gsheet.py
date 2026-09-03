# -*- coding: utf-8 -*-
"""
Pousse l'inventaire a date dans le Google Sheet, via l'Apps Script deja deploye.
================================================================================
Le connecteur Drive de Claude n'ecrit pas dans des cellules et plafonne les
creations de fichier bien en dessous de la taille de ce tableau. On reutilise
donc le meme canal que l'echeancier : un Apps Script deploye par Nicolas, qui
recoit la charge en JSON et ecrit lui-meme dans le classeur.
Cf. Teatower-Direction/tresorerie/gsheet/README.md

L'Apps Script fait `insertSheet(nom)` si l'onglet n'existe pas et ne touche QUE
les onglets presents dans la charge : les onglets Echeancier / Synthese ne
bougent pas.

    set GSHEET_URL=https://script.google.com/macros/s/AKfy..../exec
    set GSHEET_SECRET=teatower2026
    python push_stock_gsheet.py --date 2026-01-01 [--dry-run]
"""
import csv, datetime as dt, io, json, os, sys, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

DATE = '2026-01-01'
for i, a in enumerate(sys.argv):
    if a == '--date' and i + 1 < len(sys.argv):
        DATE = sys.argv[i + 1]
    elif a.startswith('--date='):
        DATE = a.split('=', 1)[1]

SRC = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Teatower', 'output',
                   f"stock_a_date_{DATE.replace('-', '')}_SHEET.csv")
if not os.path.exists(SRC):
    raise SystemExit(f"Fichier introuvable : {SRC}\n"
                     f"Lancer d'abord : python scripts/stock_a_date_par_entrepot.py --date {DATE}")

VERT = "#1F4A36"
ROUGE_F = "#FBE4E0"
ROUGE_T = "#A5331F"
GRIS = "#EDEFEE"

raw = list(csv.reader(io.open(SRC, encoding='utf-8')))
header = raw[1]
data = [r for r in raw[2:] if r and r[0] and r[0] != 'TOTAL GENERAL']
total = next((r for r in raw[2:] if r and r[0] == 'TOTAL GENERAL'), None)
NC = len(header)


def num(v):
    """Les quantites doivent partir en NOMBRES, pas en texte, sinon pas de somme
    possible dans le Sheet et le tri se fait alphabetiquement."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return v if v is not None else ""


jour = dt.datetime.strptime(DATE, '%Y-%m-%d') - dt.timedelta(days=1)
titre = (f"Stock au {dt.datetime.strptime(DATE, '%Y-%m-%d').strftime('%d/%m/%Y')} à 00:00 "
         f"(clôture du {jour.strftime('%d/%m/%Y')}) — {len(data)} références — "
         f"extrait le {dt.datetime.now().strftime('%d/%m/%Y %H:%M')}")

rows = [[titre] + [""] * (NC - 1), header]
rows += [[r[0], r[1], r[2]] + [num(x) for x in r[3:]] for r in data]
if total:
    rows.append(['TOTAL GÉNÉRAL', '', ''] + [num(x) for x in total[3:]])

first = 3
last = len(rows)
onglet = {
    "name": f"Stock {dt.datetime.strptime(DATE, '%Y-%m-%d').strftime('%d-%m-%Y')}",
    "ncols": NC,
    "rows": rows,
    "headerRow": 2,
    "firstDataRow": first,
    "headerColor": VERT,
    "freezeRows": 2,
    "filter": [2, last - (1 if total else 0)],
    "widths": [14, 46, 8] + [11] * (NC - 4) + [13],
    "numberFormats": {str(i): '#,##0.00' for i in range(4, NC + 1)},
    "titles": [[1, 1, NC]],
    "bold": [[last, 1]] if total else [],
    "conditional": [
        # une quantite negative a une date passee = incoherence de flux, pas un stock
        {"range": f"D{first}:{chr(64 + NC)}{last}",
         "formula": f'=AND(D{first}<>"",D{first}<0)',
         "background": ROUGE_F, "fontColor": ROUGE_T, "bold": True},
    ],
    "fills": [{"range": f"A{last}:{chr(64 + NC)}{last}", "background": GRIS}] if total else [],
}

charge = {"sheets": [onglet],
          "key": os.environ.get("GSHEET_SECRET", "teatower2026"),
          "stamp": dt.datetime.now().strftime("%d/%m/%Y %H:%M")}
corps = json.dumps(charge, ensure_ascii=False).encode("utf-8")

print(f"source : {SRC}")
print(f"onglet : {onglet['name']}  {len(rows)} lignes x {NC} colonnes")
print(f"charge : {len(corps) / 1024:.0f} Ko")
ctrl = sum(v for r in rows[2:(last - 1 if total else last)] for v in r[3:NC - 1]
           if isinstance(v, float))
print(f"controle somme entrepots (hors colonne TOTAL) : {ctrl:,.2f}")

if "--dry-run" in sys.argv:
    print("\n--dry-run : rien envoye.")
    raise SystemExit(0)

url = os.environ.get("GSHEET_URL")
if not url:
    raise SystemExit("Definir GSHEET_URL (URL /exec du deploiement Apps Script).")
req = urllib.request.Request(url, data=corps, method="POST",
                             headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=300) as r:
    rep = json.loads(r.read().decode("utf-8"))
if not rep.get("ok"):
    raise SystemExit(f"ECHEC : {rep.get('error')}")
print(f"-> ecrit dans le Sheet : {', '.join(rep.get('onglets', []))}")
