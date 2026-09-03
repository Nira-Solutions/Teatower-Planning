# -*- coding: utf-8 -*-
"""
Stock a date, par reference et par entrepot -- Teatower
=======================================================
Utilise le mecanisme NATIF d'Odoo : `qty_available` est un champ calcule qui
accepte dans le contexte :
    to_date      -> la quantite telle qu'elle etait a cette date/heure
    warehouse_id -> restreint le calcul a un entrepot

ATTENTION PIEGE ODOO 18 : la cle est `warehouse_id`. L'ancienne cle `warehouse` est
    SILENCIEUSEMENT IGNOREE -- elle ne leve aucune erreur et renvoie le stock
    GLOBAL pour chaque entrepot (symptome : tous les entrepots affichent le
    meme nombre de references). Toujours recaler sur une reference temoin
    contre stock.quant avant d'exploiter le fichier.
C'est exactement ce que fait le wizard "Inventaire a une date" de l'interface,
donc les chiffres sont ceux qu'Odoo afficherait a l'ecran (pas une reconstruction
maison a partir des mouvements, qui se trompe sur les conversions d'unites).

ATTENTION SEMANTIQUE DE LA DATE :
  --date 2026-01-01  =  situation a 00:00 le 01/01/2026
                     =  cloture du 31/12/2025, avant tout mouvement du 1er janvier.
  Pour la situation en FIN de journee du 01/01, passer --date 2026-01-02.

Usage : python stock_a_date_par_entrepot.py
        python stock_a_date_par_entrepot.py --date 2026-01-01
        python stock_a_date_par_entrepot.py --date 2026-01-01 --tous   (garde les lignes a 0)
"""
import os, sys, csv, xmlrpc.client
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

URL = 'https://tea-tree.odoo.com'
DB = 'tsc-be-tea-tree-main-18515272'
USER = 'nicolas.raes@teatower.com'
PWD = os.environ.get('ODOO_PWD')
if not PWD:
    raise SystemExit("Definir ODOO_PWD (repo public, jamais de mot de passe en clair).")
uid = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common').authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')


def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})


DATE = '2026-01-01'
for i, a in enumerate(sys.argv):
    if a == '--date' and i + 1 < len(sys.argv):
        DATE = sys.argv[i + 1]
    elif a.startswith('--date='):
        DATE = a.split('=', 1)[1]
datetime.strptime(DATE, '%Y-%m-%d')          # garde-fou format
TO_DATE = f'{DATE} 00:00:00'
KEEP_ZERO = '--tous' in sys.argv

OUT_DIR = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Teatower', 'output')
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, f"stock_a_date_{DATE.replace('-', '')}_par_entrepot.csv")

# --- entrepots -------------------------------------------------------------
whs = call('stock.warehouse', 'search_read', [[]], {'fields': ['id', 'name', 'code'], 'order': 'id'})
print(f"Stock au {DATE} 00:00 (= cloture de la veille) | {len(whs)} entrepots\n")

# --- produits stockables ---------------------------------------------------
try:
    prods = call('product.product', 'search_read', [[['is_storable', '=', True]]],
                 {'fields': ['id', 'default_code', 'name', 'uom_id'], 'order': 'default_code'})
except Exception:
    prods = call('product.product', 'search_read', [[['type', '=', 'product']]],
                 {'fields': ['id', 'default_code', 'name', 'uom_id'], 'order': 'default_code'})
pids = [p['id'] for p in prods]
print(f"{len(prods)} references stockables\n")

# --- lecture par entrepot, en une passe chacune ----------------------------
qty = {}     # (pid, wh_code) -> qty
for w in whs:
    ctx = {'to_date': TO_DATE, 'warehouse_id': w['id']}
    rows = call('product.product', 'read', [pids], {'fields': ['qty_available'], 'context': ctx})
    n = 0
    for r in rows:
        v = r['qty_available'] or 0.0
        if v:
            qty[(r['id'], w['code'])] = v
            n += 1
    print(f"  {w['code']:6} {w['name'][:32]:32} {n:5} references avec du stock")

# --- colonne HORS-WH + garde-fou de reconciliation --------------------------
# La base contient des emplacements internes rattaches a AUCUN entrepot
# (ex. D-16-01, MP_1v0666, NAM). Leur stock existe dans le total global mais
# n'apparait dans aucune colonne d'entrepot. On l'isole au lieu de le perdre :
#   HORS-WH (par produit) = stock global a la date - somme des entrepots
# Le fichier reconcilie ainsi toujours avec le stock global d'Odoo.
orphans = call('stock.location', 'search_read',
               [[['usage', '=', 'internal'], ['warehouse_id', '=', False]]],
               {'fields': ['id', 'complete_name']})
if orphans:
    print(f"\n  {len(orphans)} emplacement(s) interne(s) sans entrepot :")
    for o in orphans:
        print(f"    #{o['id']} {o['complete_name']}")

glob = {r['id']: (r['qty_available'] or 0.0) for r in
        call('product.product', 'read', [pids],
             {'fields': ['qty_available'], 'context': {'to_date': TO_DATE}})}
for p in prods:
    reste = round(glob.get(p['id'], 0.0) - sum(qty.get((p['id'], w['code']), 0.0) for w in whs), 3)
    if reste:
        qty[(p['id'], 'HORS-WH')] = reste

tot_glob = sum(glob.values())
tot_wh = sum(qty.values())
print(f"\n  Controle : somme des colonnes {tot_wh:,.2f} vs stock global Odoo {tot_glob:,.2f}")
if abs(tot_wh - tot_glob) > 0.5:
    raise SystemExit(f"  ECART {tot_wh - tot_glob:+,.2f} -- ventilation NON fiable, fichier non ecrit.")
print("  -> reconcilie")

# --- ecriture --------------------------------------------------------------
codes = [w['code'] for w in whs] + (['HORS-WH'] if any(k[1] == 'HORS-WH' for k in qty) else [])
lines = 0
with open(OUT, 'w', newline='', encoding='utf-8-sig') as f:
    wcsv = csv.writer(f, delimiter=';')
    wcsv.writerow([f'Stock au {DATE} 00:00 (cloture du jour precedent)'])
    wcsv.writerow([])
    wcsv.writerow(['Reference', 'Designation', 'UdM'] + codes + ['TOTAL'])
    for p in prods:
        vals = [qty.get((p['id'], c), 0.0) for c in codes]
        tot = sum(vals)
        if not KEEP_ZERO and tot == 0:
            continue
        wcsv.writerow([p['default_code'] or '', p['name'],
                       p['uom_id'][1] if p['uom_id'] else ''] +
                      [f'{v:.2f}'.replace('.', ',') for v in vals] +
                      [f'{tot:.2f}'.replace('.', ',')])
        lines += 1
    wcsv.writerow([])
    wcsv.writerow(['TOTAL GENERAL', '', ''] +
                  [f'{sum(qty.get((p["id"], c), 0.0) for p in prods):.2f}'.replace('.', ',') for c in codes] +
                  [f'{sum(qty.values()):.2f}'.replace('.', ',')])

print(f"\n{lines} references avec du stock au {DATE}")
print(f"Total toutes references / tous entrepots : {sum(qty.values()):,.2f} unites")
print(f"\nFichier : {OUT}")
