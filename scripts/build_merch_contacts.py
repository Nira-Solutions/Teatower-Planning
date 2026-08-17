"""
build_merch_contacts.py — Page "Contacts & delais" du planning MERCHANDISER (Gilles).

Lit le dernier planning_pool_*.csv (build_planning_pool.py, source OBLIGATOIRE)
et compose, pour chaque GMS merch, la personne de contact depuis DEUX sources :
  1. res.partner enfants du magasin (contacts structures)
  2. le `comment` de la fiche ("Contact merchandiser: X" / "Personne de contact :")
     -> c'est la que vit l'info pour la majorite des magasins merch.
+ notes operationnelles (jours de visite, livraison...) extraites du comment.
+ delais de visite (Tier, cycle, derniere SO, prochaine visite, retard) + filtre.

Exclut les magasins televente (perimetre Vanessa). Se comporte comme un 2e onglet
du planning merch (bouton en haut de index.html). Aucune ecriture Odoo.
"""

import csv
import html
import re
import xmlrpc.client
from collections import defaultdict
from pathlib import Path

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"
# Chemins relatifs au depot : le nom d'utilisateur Windows differe d'un poste a
# l'autre (FlowUP sur le fixe, Nraes sur le portable) -> aucun chemin en dur.
REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
OUT = REPO / "planning" / "contacts.html"

# mots qui marquent la FIN du nom de contact dans le comment (texte issu d'un
# import Sheet ou tout est colle par des espaces simples)
STOP = ["Visite", "Attention", "Demande", "Pas de", "Pas d", "Le client", "Livraison",
        "Personne", "Responsable", "n'est", "Quai", "Tel", "Tél", "GSM", "Horaire",
        "Ouvert", "Ferme", "Fermé", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi",
        "Ok ", "OK ", "ok ", "suivi", "Gérante", "Gérant", "Gerant", "pour Gilles",
        "magasin :", "Adresse", "Mail", "Email", "Commande", "Depuis", "franchise",
        "Suite", "Mag", "Au ", "Le magasin", "Demander"]
HEADER_RE = re.compile(r"-{2,}\s*Remarques merchandiser.*?-{2,}", re.I)
TAG_RE = re.compile(r"\[[^\]]*\]")
# formes precises d'abord (Contact merchandiser: / Personne de contact :),
# fallback "Contact :" AVEC deux-points (evite de matcher "recontacté ...")
CONTACT_RE = re.compile(r"(?:Contact merchandiser|Personne de contact)\s*:?\s*(.+)", re.I)
CONTACT_RE2 = re.compile(r"\bContact\s*:\s*(.+)", re.I)

CSS = """
  :root { --primary:#2d6a4f; --accent:#40916c; --bg:#f8f9fa; --card:#fff; --text:#212529; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); padding:1rem; max-width:1050px; margin:0 auto; }
  h1 { color:var(--primary); font-size:1.5rem; margin-bottom:.3rem; }
  .subtitle { color:#666; font-size:.9rem; margin-bottom:1rem; }
  .tabs { display:flex; gap:.5rem; margin-bottom:1.2rem; }
  .tab-btn { padding:.5rem 1.1rem; border-radius:6px; border:2px solid var(--primary); background:var(--card); color:var(--primary); font-weight:600; cursor:pointer; font-size:.9rem; text-decoration:none; display:inline-block; }
  .tab-btn.active { background:var(--primary); color:#fff; }
  .filter { width:100%; padding:.55rem .8rem; font-size:.95rem; border:2px solid #ddd; border-radius:8px; margin-bottom:.8rem; }
  table.c { width:100%; border-collapse:collapse; font-size:.82rem; background:var(--card); border-radius:8px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.1); }
  table.c th { background:var(--primary); color:#fff; text-align:left; padding:.5rem .55rem; font-size:.72rem; text-transform:uppercase; }
  table.c td { padding:.45rem .55rem; border-bottom:1px solid #eee; vertical-align:top; }
  table.c tr:hover td { background:#eef6f1; }
  .cname { font-weight:600; }
  .person { font-weight:600; color:#1864ab; }
  .cmiss { color:#c92a2a; font-style:italic; }
  .notes { color:#666; font-size:.78rem; }
  .tier { font-weight:700; padding:1px 6px; border-radius:3px; }
  .tA{background:#d3f9d8;color:#2b8a3e} .tB{background:#e7f5ff;color:#1864ab} .tC{background:#fff3bf;color:#b08400} .tX{background:#e9ecef;color:#495057}
  .ret { color:#c92a2a; font-weight:700; }
  .stArret{color:#c92a2a} .stNoMerch{color:#868e96}
  @media(max-width:600px){ table.c{ font-size:.72rem; } }
"""
JS = "function f(){var q=document.getElementById('cf').value.toLowerCase();document.querySelectorAll('#t tbody tr').forEach(function(r){r.style.display=r.innerText.toLowerCase().indexOf(q)>-1?'':'none';});}"


def esc(s):
    return html.escape(str(s)) if s else ""


def clean(comment):
    """comment HTML -> texte plat sans header import ni tags [..]."""
    t = re.sub(r"<[^>]+>", " ", str(comment or ""))
    t = HEADER_RE.sub(" ", t)
    t = TAG_RE.sub(" ", t)
    t = re.sub(r"📍", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def contact_from_comment(comment):
    """Extrait le nom de contact ('Contact merchandiser: X') du comment, sinon ''."""
    t = re.sub(r"<[^>]+>", " ", str(comment or ""))
    t = HEADER_RE.sub(" ", t)
    t = re.sub(r"📍[^\n]*?(?=Contact|Personne|$)", " ", t)  # vire le "📍 <nom magasin>"
    m = CONTACT_RE.search(t) or CONTACT_RE2.search(t)
    if not m:
        return ""
    rest = re.sub(r"\s+", " ", m.group(1)).strip()
    rest = re.sub(r"^(magasin|pdv|point de vente)\s*:?\s*", "", rest, flags=re.I)
    # coupe au 1er mot-stop / tag / ponctuation
    cut = len(rest)
    for w in STOP:
        i = rest.find(w)
        if 0 <= i < cut:
            cut = i
    for ch in "[.;(=>":
        i = rest.find(ch)
        if 0 <= i < cut:
            cut = i
    name = rest[:cut].strip(" -:,/")
    return name[:40]


def main():
    cands = sorted(DATA.glob("planning_pool_*.csv"))
    if not cands:
        raise SystemExit("Aucun planning_pool_*.csv — lance d'abord build_planning_pool.py")
    csv_path = cands[-1]
    stamp = csv_path.stem.replace("planning_pool_", "")
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    rows = [r for r in rows if r.get("statut") != "Televente"]  # perimetre Gilles

    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    pids = [int(r["pid"]) for r in rows]

    # contacts structures (enfants)
    contacts = []
    for i in range(0, len(pids), 200):
        contacts += models.execute_kw(DB, uid, PASSWORD, "res.partner", "search_read",
            [[("parent_id", "in", pids[i:i + 200])]],
            {"fields": ["parent_id", "name", "function", "phone", "mobile", "email"]})
    cmap = defaultdict(list)
    for c in contacts:
        if c.get("parent_id"):
            cmap[c["parent_id"][0]].append(c)

    # comments des magasins (2e source de contact + notes)
    commap = {}
    for i in range(0, len(pids), 200):
        for p in models.execute_kw(DB, uid, PASSWORD, "res.partner", "read",
                                   [pids[i:i + 200]], {"fields": ["comment"]}):
            commap[p["id"]] = p.get("comment") or ""

    def contact_cell(pid, r):
        """(nom_html, tel, email, notes) en combinant enfants + comment."""
        cs = [c for c in cmap.get(pid, []) if (c.get("name") or "").strip()]
        comment = commap.get(pid, "")
        notes = clean(comment)
        if cs:
            cs.sort(key=lambda c: (0 if c.get("function") else 1, 0 if (c.get("phone") or c.get("mobile")) else 1))
            names = ", ".join((c["name"] + (f" ({c['function']})" if c.get("function") else "")) for c in cs)
            tel = next((c.get("phone") or c.get("mobile") for c in cs if c.get("phone") or c.get("mobile")), None) or r.get("phone") or ""
            mail = next((c.get("email") for c in cs if c.get("email")), None) or r.get("email") or ""
            return (f'<span class="person">{esc(names)}</span>', tel, mail, notes)
        # fallback : nom dans le comment
        cn = contact_from_comment(comment)
        if cn:
            return (f'<span class="person">{esc(cn)}</span>', r.get("phone") or "", r.get("email") or "", notes)
        return ('<span class="cmiss">à compléter</span>', r.get("phone") or "", r.get("email") or "", notes)

    actifs = [r for r in rows if r["statut"] == "Actif"]
    body = ['<input class="filter" id="cf" onkeyup="f()" placeholder="🔎 Filtrer (magasin, contact, ville, tél, notes…)">']
    body.append(f'<p style="font-size:.82rem;color:#666;margin-bottom:.6rem">{len(rows)} magasins GMS '
                f'({len(actifs)} actifs) — contact (fiche + comment Odoo) & délais de visite.</p>')
    body.append('<table class="c" id="t"><thead><tr>'
                '<th>Magasin</th><th>Contact</th><th>Tél</th><th>Email</th><th>Notes</th>'
                '<th>Ville</th><th>Statut</th><th>Tier</th><th>Cycle</th><th>Dern. SO</th>'
                '<th>Proch. visite</th><th>Retard</th></tr></thead><tbody>')
    for r in sorted(rows, key=lambda r: (r["statut"] != "Actif", r["display_name"].lower())):
        pid = int(r["pid"])
        name_html, tel, mail, notes = contact_cell(pid, r)
        cell_tel = esc(tel) if tel else '<span class="cmiss">?</span>'
        tier = r["tier"]
        retard = int(r["retard_j"]) if r["retard_j"] else 0
        ret_cell = f'<span class="ret">{retard}j</span>' if retard > 0 else "—"
        st = r["statut"]
        st_cls = {"Arret": "stArret", "NoMerch": "stNoMerch"}.get(st, "")
        body.append(f'<tr><td class="cname">{esc(r["display_name"])} <span style="color:#aaa">#{r["pid"]}</span></td>'
                    f'<td>{name_html}</td><td>{cell_tel}</td><td>{esc(mail)}</td>'
                    f'<td class="notes">{esc(notes[:140])}</td>'
                    f'<td>{esc(r["city"])}</td><td class="{st_cls}">{esc(st)}</td>'
                    f'<td><span class="tier t{tier}">{tier}</span></td><td>{esc(r["cycle_days"])}j</td>'
                    f'<td>{esc(r["last_so_label"])}</td><td>{esc(r["next_visit"])}</td><td>{ret_cell}</td></tr>')
    body.append('</tbody></table>')

    page = f"""<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Contacts & délais — Planning Merchandiser Teatower</title>
<style>{CSS}</style></head><body>
<h1>Contacts & délais — Merchandiser</h1>
<p class="subtitle">Gilles &nbsp;|&nbsp; tous les GMS suivis &nbsp;|&nbsp; généré le {stamp}</p>
<div class="tabs">
  <a class="tab-btn" href="index.html">📅 Planning</a>
  <a class="tab-btn active" href="contacts.html">📇 Contacts & délais</a>
</div>
{''.join(body)}
<script>{JS}</script></body></html>"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    named = sum(1 for r in rows if 'à compléter' not in contact_cell(int(r["pid"]), r)[0])
    print(f"[+] {OUT}")
    print(f"    {len(rows)} magasins | {named} avec contact (fiche+comment) | {len(rows)-named} à compléter")


if __name__ == "__main__":
    main()
