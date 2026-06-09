"""
build_merch_contacts.py — Page "Contacts & delais" du planning MERCHANDISER (Gilles).

Lit le dernier planning_pool_*.csv (produit par build_planning_pool.py, source
OBLIGATOIRE) et ajoute la personne de contact (res.partner enfants du magasin),
puis rend planning/contacts.html : liste de TOUS les GMS merch avec contact +
delais de visite (Tier, cycle, derniere SO, prochaine visite, retard) + filtre.

Se comporte comme un 2e onglet du planning merch (bouton en haut de index.html).
Aucune ecriture Odoo, aucun mail, aucun calendrier.

Usage : python build_merch_contacts.py
"""

import csv
import html
import xmlrpc.client
from datetime import date
from collections import defaultdict
from pathlib import Path

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"
DATA = Path(r"C:\Users\FlowUP\OneDrive\Teatower\data")
OUT = Path(r"C:\Users\FlowUP\OneDrive\Teatower-Planning\planning\contacts.html")

CSS = """
  :root { --primary:#2d6a4f; --accent:#40916c; --bg:#f8f9fa; --card:#fff; --text:#212529; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); padding:1rem; max-width:1000px; margin:0 auto; }
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
  .cmiss { color:#c92a2a; font-style:italic; }
  .tier { font-weight:700; padding:1px 6px; border-radius:3px; }
  .tA{background:#d3f9d8;color:#2b8a3e} .tB{background:#e7f5ff;color:#1864ab} .tC{background:#fff3bf;color:#b08400} .tX{background:#e9ecef;color:#495057}
  .ret { color:#c92a2a; font-weight:700; }
  .stArret{color:#c92a2a} .stNoMerch{color:#868e96}
  @media(max-width:600px){ table.c{ font-size:.72rem; } }
"""

JS = "function f(){var q=document.getElementById('cf').value.toLowerCase();document.querySelectorAll('#t tbody tr').forEach(function(r){r.style.display=r.innerText.toLowerCase().indexOf(q)>-1?'':'none';});}"


def esc(s):
    return html.escape(str(s)) if s else ""


def main():
    cands = sorted(DATA.glob("planning_pool_*.csv"))
    if not cands:
        raise SystemExit("Aucun planning_pool_*.csv — lance d'abord build_planning_pool.py")
    csv_path = cands[-1]
    stamp = csv_path.stem.replace("planning_pool_", "")
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    # Perimetre Gilles : on exclut les magasins televente (suivi Vanessa par appels)
    rows = [r for r in rows if r.get("statut") != "Televente"]

    # contacts rattaches
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    pids = [int(r["pid"]) for r in rows]
    contacts = []
    for i in range(0, len(pids), 200):
        contacts += models.execute_kw(DB, uid, PASSWORD, "res.partner", "search_read",
            [[("parent_id", "in", pids[i:i + 200])]],
            {"fields": ["parent_id", "name", "function", "phone", "mobile", "email"]})
    cmap = defaultdict(list)
    for c in contacts:
        if c.get("parent_id"):
            cmap[c["parent_id"][0]].append(c)

    def best(pid, r):
        """Liste TOUS les contacts nommes (joints), + tel/email du 1er dispo / societe."""
        cs = [c for c in cmap.get(pid, []) if (c.get("name") or "").strip()]
        if not cs:
            return ("", "", r.get("phone") or "", r.get("email") or "")
        cs.sort(key=lambda c: (0 if c.get("function") else 1, 0 if (c.get("phone") or c.get("mobile")) else 1))
        names = ", ".join((c["name"] + (f" ({c['function']})" if c.get("function") else "")) for c in cs)
        funcs = ", ".join(c["function"] for c in cs if c.get("function"))
        tel = next((c.get("phone") or c.get("mobile") for c in cs if c.get("phone") or c.get("mobile")), None) or r.get("phone") or ""
        mail = next((c.get("email") for c in cs if c.get("email")), None) or r.get("email") or ""
        return (names, funcs, tel, mail)

    actifs = [r for r in rows if r["statut"] == "Actif"]
    body = [f'<input class="filter" id="cf" onkeyup="f()" placeholder="🔎 Filtrer (magasin, contact, ville, tél, tier…)">']
    body.append(f'<p style="font-size:.82rem;color:#666;margin-bottom:.6rem">{len(rows)} magasins GMS '
                f'({len(actifs)} actifs) — délais de visite = Tier / cycle / prochaine visite / retard.</p>')
    body.append('<table class="c" id="t"><thead><tr>'
                '<th>Magasin</th><th>Contact</th><th>Fonction</th><th>Tél</th><th>Email</th>'
                '<th>Ville</th><th>Statut</th><th>Tier</th><th>Cycle</th><th>Dernière SO</th>'
                '<th>Proch. visite</th><th>Retard</th></tr></thead><tbody>')
    for r in sorted(rows, key=lambda r: (r["statut"] != "Actif", r["display_name"].lower())):
        pid = int(r["pid"])
        name, func, tel, mail = best(pid, r)
        cell_name = esc(name) if name else '<span class="cmiss">à compléter</span>'
        cell_tel = esc(tel) if tel else '<span class="cmiss">?</span>'
        tier = r["tier"]
        retard = int(r["retard_j"]) if r["retard_j"] else 0
        ret_cell = f'<span class="ret">{retard}j</span>' if retard > 0 else "—"
        st = r["statut"]
        st_cls = {"Arret": "stArret", "NoMerch": "stNoMerch"}.get(st, "")
        body.append(f'<tr><td class="cname">{esc(r["display_name"])} <span style="color:#aaa">#{r["pid"]}</span></td>'
                    f'<td>{cell_name}</td><td>{esc(func)}</td><td>{cell_tel}</td><td>{esc(mail)}</td>'
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
    named = sum(1 for r in rows if best(int(r["pid"]), r)[0])
    print(f"[+] {OUT}")
    print(f"    {len(rows)} magasins | {named} avec contact nomme | source planning_pool_{stamp}.csv")


if __name__ == "__main__":
    main()
