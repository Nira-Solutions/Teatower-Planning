"""Pose les tags [VISITE AAAA-MM-JJ] manquants — lot Renato 17/08 -> 26/08/2026.

REGLES §14 : une visite SANS reassort ne laisse ni commande ni picking dans Odoo.
La seule trace est le canal Slack #merchandiser (C08LK3W76S1). Le lot poste par
Renato entre le 17/08 et le 26/08 n'avait jamais ete importe : les 4 magasins
ci-dessous ressortaient OVERDUE a tort dans planning_pool_2026-09-06.

Controle : Delhaize Rixensart (#50967) est explicitement « pas fait » le 26/08 —
AUCUN tag pose, le magasin reste a juste titre en retard (planifie en S37).

Le mot de passe est lu dans ODOO_PWD (repo public — jamais de secret en clair).

Usage: python scripts/slack_visites_vers_odoo_20260906.py [--apply]
"""
import os
import re
import sys
import xmlrpc.client

URL = 'https://tea-tree.odoo.com'
DB = 'tsc-be-tea-tree-main-18515272'
USER = 'nicolas.raes@teatower.com'
PWD = os.environ['ODOO_PWD']
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')


def call(m, meth, a, k=None):
    return models.execute_kw(DB, uid, PWD, m, meth, a, k or {})


APPLY = '--apply' in sys.argv

# (pid, date de passage, libelle Slack, issue)
VISITES = [
    (123297, "2026-08-17", "Spar Gembloux",            "pas besoin de remplir (Renato)"),
    (2924,   "2026-08-17", "Delhaize Incourt",         "pas besoin de remplir (Renato)"),
    (9046,   "2026-08-19", "Hyper Carrefour Jambes",   "pas besoin de commande, reste du stock chez eux (Renato)"),
    (5830,   "2026-08-26", "Proxy Delhaize Bosvoorde", "pas besoin de remplir (Renato)"),
]

TAG_RE = re.compile(r"\[VISITE (\d{4}-\d{2}-\d{2})", re.IGNORECASE)

print("MODE :", "APPLY" if APPLY else "DRY-RUN")
for pid, d, libelle, issue in VISITES:
    r = call('res.partner', 'read', [[pid]], {'fields': ['name', 'comment']})[0]
    txt = re.sub(r'<[^>]+>', ' ', str(r['comment'] or ''))
    if d in TAG_RE.findall(txt):
        print(f"=  #{pid:7} {str(r['name'])[:38]:38} [VISITE {d}] deja pose")
        continue
    tag = f"<p>[VISITE {d} — sans réassort] {libelle} — {issue} (source Slack #merchandiser)</p>"
    print(f"+  #{pid:7} {str(r['name'])[:38]:38} [VISITE {d}]  {issue[:45]}")
    if APPLY:
        call('res.partner', 'write', [[pid], {'comment': (r['comment'] or '') + tag}])

# Spar Namur (#122958) : passage du 03/09 ECHOUE (stationnement impossible, zone
# pietonne). Ce n'est PAS une visite -> aucun tag [VISITE], juste la trace du
# rendez-vous manque pour que le magasin reste prioritaire.
PID_SPAR = 122958
NOTE = ("<p>[PASSAGE MANQUE 2026-09-03] Gilles n'a pas pu se garer (zone pietonne). "
        "Aucun reassort effectue — magasin replanifie le MATIN en S37.</p>")
r = call('res.partner', 'read', [[PID_SPAR]], {'fields': ['name', 'comment']})[0]
if "PASSAGE MANQUE 2026-09-03" in str(r['comment'] or ''):
    print(f"=  #{PID_SPAR:7} {str(r['name'])[:38]:38} note passage manque deja posee")
else:
    print(f"+  #{PID_SPAR:7} {str(r['name'])[:38]:38} note [PASSAGE MANQUE 2026-09-03]")
    if APPLY:
        call('res.partner', 'write', [[PID_SPAR], {'comment': (r['comment'] or '') + NOTE}])
