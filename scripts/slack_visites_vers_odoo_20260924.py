"""Pose les tags [VISITE AAAA-MM-JJ] dans Odoo depuis le canal Slack #merchandiser.

Une visite SANS reassort ne laisse ni commande ni picking dans Odoo : le magasin
passe pour jamais visite et le garde-fou §14 le bascule a tort en televente.
La seule trace de ces passages est le canal Slack #merchandiser (C08LK3W76S1),
ou Gilles et Renato postent chaque magasin avec « Pas besoin de remplir ».

Ce script pose le tag que build_planning_pool.py sait deja lire.
Source : lecture du canal (MCP Slack), passages du 22 au 24/09/2026 (import quotidien en panne : token_expired depuis le 18/09).

Usage: python scripts/slack_visites_vers_odoo.py [--apply]
"""
import os
import re, sys, xmlrpc.client
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD=os.environ["ODOO_PWD"]
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})
APPLY='--apply' in sys.argv

# (pid, date de passage, libelle Slack, issue)
VISITES = [
    (6999,   "2026-09-22", "Hyper Carrefour Marche",        "livraison display ok (Renato)"),
    (2952,   "2026-09-22", "AD Delhaize Fernelmont",        "passage ok (Renato)"),
    (5755,   "2026-09-22", "Intermarche Naninne",           "passage ok (Renato)"),
    (2773,   "2026-09-22", "Carrefour Market Ciney",        "passage ok (Renato)"),
    (2811,   "2026-09-22", "Carrefour Market Barvaux",      "passage ok (Renato)"),
    (119817, "2026-09-22", "Delhaize Barvaux",              "passage ok (Renato)"),
    (119819, "2026-09-22", "Delhaize Hotton",               "pas besoin de remplir (Renato)"),
    (2979,   "2026-09-22", "Carrefour Market Hotton",       "passage ok (Renato)"),
    (121818, "2026-09-23", "Hyper Carrefour Ans",           "pas besoin de remplir (Renato)"),
    (113627, "2026-09-23", "Carrefour Market Grace-Hollogne","passage ok (Renato)"),
    (7760,   "2026-09-23", "Hyper Carrefour Fleron",        "responsable pas present (Renato)"),
    (126113, "2026-09-23", "Delhaize Esneux",               "pas besoin de remplir (Renato)"),
    (116869, "2026-09-23", "Intermarche Tilff",             "pas besoin de remplir (Renato)"),
    (5878,   "2026-09-23", "Carrefour Market Remouchamps",  "passage ok (Renato)"),
    (9046,   "2026-09-24", "Hyper Carrefour Jambes",        "pas besoin de remplir (Gilles)"),
    (114704, "2026-09-24", "Delhaize Salzinnes",            "passage (Gilles)"),
]

TAG_RE = re.compile(r"\[VISITE (\d{4}-\d{2}-\d{2})", re.IGNORECASE)

for pid, d, libelle, issue in VISITES:
    r = call('res.partner','read',[[pid]],{'fields':['display_name','comment']})[0]
    txt = re.sub(r'<[^>]+>', ' ', str(r['comment'] or ''))
    if d in TAG_RE.findall(txt):
        print(f"=  #{pid:7} {r['display_name'][:38]:38} [VISITE {d}] deja pose"); continue
    tag = f"<p>[VISITE {d} — sans réassort] {libelle} — {issue} (source Slack #merchandiser)</p>"
    print(f"+  #{pid:7} {r['display_name'][:38]:38} [VISITE {d}]  {issue[:40]}")
    if APPLY:
        call('res.partner','write',[[pid],{'comment':(r['comment'] or '')+tag}])

print('\n' + ('APPLIQUE.' if APPLY else 'DRY-RUN (--apply pour ecrire).'))
