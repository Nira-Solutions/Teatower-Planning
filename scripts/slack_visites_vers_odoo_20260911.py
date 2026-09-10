# -*- coding: utf-8 -*-
"""Tags [VISITE] depuis Slack #merchandiser — passages des 07 et 08/09/2026.

Croise avec Odoo : seuls les magasins SANS commande depuis le 07/09 sont tagues
(Proxy Lillois #114763 a genere S06332, il garde sa trace naturelle).
Le vendredi 11/09 n'est pas traite : la tournee est en cours, rien n'est encore
poste dans Slack.

Usage : python scripts/slack_visites_vers_odoo_20260911.py [--apply]
"""
import os, re, sys, xmlrpc.client
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = os.environ["ODOO_PWD"]
uid = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")
def call(mo, me, a, k=None): return _m.execute_kw(DB, uid, PWD, mo, me, a, k or {})
APPLY = "--apply" in sys.argv

VISITES = [
    (9046,   "2026-09-07", "Hyper Carrefour Jambes",      "commande Noel a encoder des dispo (Gilles)"),
    (113498, "2026-09-07", "Delhaize Materne",            "pas besoin de remplir (Gilles)"),
    (114704, "2026-09-07", "Delhaize Salzinnes",          "pas besoin de remplir (Gilles)"),
    (5755,   "2026-09-07", "Intermarche Naninne",         "pas besoin de remplir (Gilles)"),
    (3209,   "2026-09-07", "Intermarche Assesse",         "passage fait, photo rayon postee (Gilles)"),
    (7679,   "2026-09-07", "AD Ciney",                    "pas besoin de remplir (Gilles)"),
    (123302, "2026-09-07", "Spar Erezee",                 "pas besoin de remplir, repasser des dispo Noel (Gilles)"),
    (8689,   "2026-09-08", "Hyper Carrefour Wavre",       "pas besoin de remplir (Gilles)"),
    (6821,   "2026-09-08", "Carrefour Market Waterloo",   "pas besoin de remplir (Gilles)"),
    (9461,   "2026-09-08", "Proxy Delhaize Saint Michel", "pas besoin de remplir (Gilles)"),
    (5729,   "2026-09-08", "Delhaize Debroux",            "pas besoin de remplir (Gilles)"),
    (123997, "2026-09-08", "AD Delhaize Roodebeek",       "pas besoin de remplir (Gilles)"),
    (50967,  "2026-09-08", "Proxy Delhaize Rixensart",    "pas besoin de remplir (Gilles)"),
]

# Renseignements terrain remontes par Gilles, au format des tags REGLES §7
TERRAIN = [
    (123302, "[REGLE: pas les lundis ni les mardis — responsable absent]"),
    (5729,   "[REGLE: contrôle marchandise obligatoire — pas d'appareil de commande sur place]"),
    (5729,   "[STOCK: pas de réserve — tout en rayon]"),
]

TAG_RE = re.compile(r"\[VISITE (\d{4}-\d{2}-\d{2})", re.IGNORECASE)
print("MODE :", "APPLY" if APPLY else "DRY-RUN")

for pid, d, libelle, issue in VISITES:
    r = call("res.partner", "read", [[pid]], {"fields": ["name", "display_name", "comment"]})[0]
    txt = re.sub(r"<[^>]+>", " ", str(r["comment"] or ""))
    if d in TAG_RE.findall(txt):
        print("=  #%-7d %-40s [VISITE %s] deja pose" % (pid, (r["name"] or r.get("display_name") or "?")[:40], d)); continue
    tag = "<p>[VISITE %s — sans réassort] %s — %s (source Slack #merchandiser)</p>" % (d, libelle, issue)
    print("+  #%-7d %-40s [VISITE %s]  %s" % (pid, (r["name"] or r.get("display_name") or "?")[:40], d, issue[:44]))
    if APPLY:
        call("res.partner", "write", [[pid], {"comment": (r["comment"] or "") + tag}])

print()
for pid, tag in TERRAIN:
    r = call("res.partner", "read", [[pid]], {"fields": ["name", "display_name", "comment"]})[0]
    txt = re.sub(r"<[^>]+>", " ", str(r["comment"] or ""))
    cle = tag.split(":")[0] + ":"
    if cle in txt and tag[1:12].lower() in txt.lower():
        print("=  #%-7d %-40s %s deja present" % (pid, (r["name"] or r.get("display_name") or "?")[:40], cle)); continue
    print("+  #%-7d %-40s %s" % (pid, (r["name"] or r.get("display_name") or "?")[:40], tag[:60]))
    if APPLY:
        call("res.partner", "write", [[pid], {"comment": (r["comment"] or "") + "<p>%s</p>" % tag}])
