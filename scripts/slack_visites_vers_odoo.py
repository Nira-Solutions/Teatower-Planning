"""Pose les tags [VISITE AAAA-MM-JJ] dans Odoo depuis le canal Slack #merchandiser.

Une visite SANS reassort ne laisse ni commande ni picking dans Odoo : le magasin
passe pour jamais visite et le garde-fou §14 le bascule a tort en televente.
La seule trace de ces passages est le canal Slack #merchandiser (C08LK3W76S1),
ou Gilles et Renato postent chaque magasin avec « Pas besoin de remplir ».

Ce script pose le tag que build_planning_pool.py sait deja lire.
Source : lecture du canal (MCP Slack), passages du 16/07 au 01/09/2026.

Usage: python scripts/slack_visites_vers_odoo.py [--apply]
"""
import re, sys, xmlrpc.client
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})
APPLY='--apply' in sys.argv

# (pid, date de passage, libelle Slack, issue)
# Perimetre : les 9 magasins bascules a tort le 02/09 + Delhaize Ath (controle).
VISITES = [
    (8779,   "2026-08-19", "Delhaize Le Beau Rivage",   "pas besoin de remplir (Renato)"),
    (7760,   "2026-08-12", "Hyper Carrefour Fleron",    "passage ok, pas de nouvelle commande (Renato)"),
    (59558,  "2026-08-10", "Carrefour Market La Chasse","pas besoin de remplir (Gilles)"),
    (3153,   "2026-08-10", "Intermarche Nivelles",      "pas besoin de remplir (Gilles)"),
    (2971,   "2026-08-04", "Intermarche Gerpinnes",     "stop pour le moment, contact a reprendre (Gilles)"),
    (113216, "2026-08-07", "Spar Louvain-la-Neuve",     "pas besoin de remplir, ete calme (Gilles)"),
    (5426,   "2026-08-10", "Delhaize Boondael",         "pas besoin de remplir (Gilles)"),
    (2773,   "2026-08-14", "Carrefour Market Ciney",    "pas besoin de remplir (Gilles)"),
    (115578, "2026-08-14", "Delhaize Andenne",          "pas besoin de remplir (Gilles)"),
]

TAG_RE = re.compile(r"\[VISITE (\d{4}-\d{2}-\d{2})", re.IGNORECASE)

for pid, d, libelle, issue in VISITES:
    r = call('res.partner','read',[[pid]],{'fields':['name','comment']})[0]
    txt = re.sub(r'<[^>]+>', ' ', str(r['comment'] or ''))
    if d in TAG_RE.findall(txt):
        print(f"=  #{pid:7} {r['name'][:38]:38} [VISITE {d}] deja pose"); continue
    tag = f"<p>[VISITE {d} — sans réassort] {libelle} — {issue} (source Slack #merchandiser)</p>"
    print(f"+  #{pid:7} {r['name'][:38]:38} [VISITE {d}]  {issue[:40]}")
    if APPLY:
        call('res.partner','write',[[pid],{'comment':(r['comment'] or '')+tag}])

print('\n' + ('APPLIQUE.' if APPLY else 'DRY-RUN (--apply pour ecrire).'))
