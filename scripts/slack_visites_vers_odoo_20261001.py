"""Pose les tags [VISITE AAAA-MM-JJ] dans Odoo depuis le canal Slack #merchandiser.

Une visite SANS reassort ne laisse ni commande ni picking dans Odoo : le magasin
passe pour jamais visite et le garde-fou §14 le bascule a tort en televente.
La seule trace de ces passages est le canal Slack #merchandiser (C08LK3W76S1),
ou Gilles et Renato postent chaque magasin avec « Pas besoin de remplir ».

Ce script pose le tag que build_planning_pool.py sait deja lire.
Source : lecture du canal (MCP Slack), passages du 29/09 au 01/10/2026 (import quotidien en panne : token_expired).

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
    (6999,   "2026-09-29", "Hyper Carrefour Marche",        "installation display ; Noel a installer fin oct./debut nov. (Gilles)"),
    (7693,   "2026-09-29", "AD Rochefort",                  "pas besoin de remplir (Gilles)"),
    (116008, "2026-09-29", "Delhaize Beauraing",            "pas besoin de remplir (Gilles)"),
    (123069, "2026-09-29", "Carrefour Market Bievre",       "pas besoin de remplir ; le responsable commande par mail (Gilles)"),
    (8779,   "2026-09-29", "Proxy Delhaize Le Beau Rivage", "pas besoin de remplir (Gilles)"),
    (5750,   "2026-09-29", "Intermarche Assesse",           "pas besoin de remplir (Gilles)"),
    (123842, "2026-09-29", "Spar Barvaux",                  "pas besoin de remplir (Gilles)"),
    (2909,   "2026-09-30", "Delhaize Embourg",              "passage ok ; retrait d'un display au prochain passage -> retours (Renato)"),
    (115578, "2026-09-30", "Delhaize Andenne",              "passage ok (Renato)"),
    (2958,   "2026-09-30", "Intermarche Floriffoux",        "passage ok (Renato)"),
    (113498, "2026-10-01", "Delhaize Materne",              "reprise thes glaces ; Noel + Halloween quand ok pour eux (Gilles)"),
    (3297,   "2026-10-01", "Intermarche Bouge",             "reprise notee ; Noel + Halloween quand ok (Gilles)"),
    (2821,   "2026-10-01", "Intermarche Belgrade",          "reprise notee ; installation Noel + Halloween (Gilles)"),
    (5484,   "2026-10-01", "Carrefour Market Uccle Bascule","pas de responsable : reprise glaces + Noel/Halloween A REFAIRE (Gilles)"),
    (5825,   "2026-10-01", "Carrefour Market Woluwe",       "reprise notee ; introduction Noel + Halloween (Gilles)"),
    (5582,   "2026-10-01", "Delhaize Genval",               "STOP pour le moment : Mr Zanoni en conge, analyse des ventes a son retour (Gilles)"),
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
