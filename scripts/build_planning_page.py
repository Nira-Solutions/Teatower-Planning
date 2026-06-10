# -*- coding: utf-8 -*-
"""
build_planning_page.py — Rendu ÉPURÉ du planning merchandiser (REGLES §8).

Génère planning/index.html à partir de données structurées par semaine/jour/stop.
Format épuré (Nicolas 10/06/2026) : PAS de récap/réflexion en haut, ligne magasin =
Heure+badge+SO · Nom+dernière SO · Adresse · Contact · [CONTROLE STOCK] · [METHODE
REASSORT] · [REGLE MAGASIN] (ces 3 uniquement si renseignés) · lien Google Maps.
Bandeau jour minimal (date, nb stops, zone, retour OK<=17:00).

Les 3 champs terrain viennent des tags Odoo (voir build_planning_pool.py) ; ici on
les passe explicitement par stop quand ils sont connus, sinon vides (=> non affichés).
"""
from urllib.parse import quote
from pathlib import Path

BASE = "5377 Baillonville"
OUT = Path(__file__).resolve().parent.parent / "planning" / "index.html"


def gmaps_one(dest):
    return f"https://www.google.com/maps/dir/?api=1&destination={quote(dest)}"


def gmaps_chain(addrs):
    return "https://www.google.com/maps/dir/" + "/".join(quote(a) for a in addrs)


def stop_html(s):
    badges = ""
    kind = s.get("k", "visite")
    if kind == "impl":
        badges += '<span class="badge badge-implantation">Implantation</span>'
    elif kind == "livr":
        badges += '<span class="badge" style="background:#0d6efd;color:#fff;">Livraison</span>'
    else:
        badges += '<span class="badge badge-visite">Visite</span>'
    for b in s.get("b", []):
        cls = "badge-overdue" if "OVERDUE" in b else "badge-priorite"
        badges += f' <span class="badge {cls}">{b}</span>'
    so = f'<span class="so">{s["so"]}</span>' if s.get("so") else ""
    # dernière SO badge
    lastso = ""
    if s.get("ls"):
        lastso = f' <span class="last-so last-so-{s.get("lsc","mid")}">{s["ls"]}</span>'
    fields = ""
    if s.get("note"):
        fields += f'<div class="opnote">{s["note"]}</div>'
    if s.get("st"):
        fields += f'<div class="field field-stock"><span class="lbl">CONTROLE STOCK :</span> {s["st"]}</div>'
    if s.get("re"):
        fields += f'<div class="field field-reassort"><span class="lbl">METHODE REASSORT :</span> {s["re"]}</div>'
    if s.get("rg"):
        fields += f'<div class="field field-regle"><span class="lbl">REGLE MAGASIN :</span> {s["rg"]}</div>'
    contact = f'<div class="contact-badge">{s["c"]}</div>' if s.get("c") else ""
    return f"""  <div class="visit">
    <div class="visit-header">
      <span><span class="time">{s["t"]}</span> {badges}</span>
      {so}
    </div>
    <div class="client">{s["n"]}{lastso}</div>
    <div class="addr">{s["a"]}</div>
    {contact}
    {fields}
    <div class="route"><a href="{gmaps_one(s["a"])}" target="_blank">Itinéraire Google Maps</a></div>
  </div>
"""


def day_html(d):
    stops = "".join(stop_html(s) for s in d["stops"])
    route = ""
    if d.get("addrs"):
        chain = gmaps_chain([BASE] + d["addrs"] + [BASE])
        route = (f'  <div class="dayroute"><strong>Trajet complet :</strong> ~{d.get("km","?")} km · '
                 f'retour Baillonville <strong>{d.get("ret","?")}</strong> ✓ ≤17:00 · '
                 f'<a href="{chain}" target="_blank">🗺️ Google Maps tournée complète</a></div>\n')
    return f"""<div class="day">
  <div class="day-header"><span>{d["h"]} — {d["sub"]}</span><span class="zone">{d["zone"]} · retour {d.get("ret","?")} OK ≤17:00</span></div>
{stops}{route}</div>
"""


def week_html(w):
    note = f'<div class="weeknote">{w["note"]}</div>\n' if w.get("note") else ""
    days = "".join(day_html(d) for d in w["days"])
    disp = "" if w.get("active") else ' style="display:none;"'
    return f'<div id="{w["id"]}"{disp}>\n<h2 class="section-title">{w["title"]}</h2>\n{note}{days}</div><!-- /{w["id"]} -->\n'


CSS = """  :root { --primary: #2d6a4f; --accent: #40916c; --warn: #e76f51; --bg: #f8f9fa; --card: #fff; --text: #212529; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); padding: 1rem; max-width: 900px; margin: 0 auto; }
  h1 { color: var(--primary); font-size: 1.4rem; margin-bottom: .3rem; }
  .subtitle { color: #666; font-size: .9rem; margin-bottom: 1rem; }
  .week-nav { display: flex; gap: .5rem; margin-bottom: 1.2rem; flex-wrap: wrap; }
  .week-btn { padding: .5rem 1rem; border-radius: 6px; border: 2px solid var(--primary); background: var(--card); color: var(--primary); font-weight: 600; cursor: pointer; text-decoration: none; font-size: .85rem; }
  .week-btn.active { background: var(--primary); color: #fff; }
  .section-title { font-size: 1.2rem; color: var(--primary); margin: 1rem 0 .5rem; border-bottom: 2px solid var(--accent); padding-bottom: .3rem; }
  .weeknote { font-size: .82rem; color: #555; background: #eef6f1; border-left: 3px solid var(--accent); padding: .4rem .7rem; border-radius: 0 4px 4px 0; margin-bottom: 1rem; }
  .day { background: var(--card); border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,.1); margin-bottom: 1rem; overflow: hidden; }
  .day-header { background: var(--primary); color: #fff; padding: .6rem 1rem; font-weight: 600; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: .3rem; }
  .day-header .zone { font-weight: 400; font-size: .82rem; opacity: .85; }
  .visit { padding: .7rem 1rem; border-bottom: 1px solid #eee; }
  .visit:last-child { border-bottom: none; }
  .visit-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: .3rem; }
  .time { font-weight: 600; color: var(--primary); min-width: 110px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: .7rem; font-weight: 600; text-transform: uppercase; }
  .badge-implantation { background: #e76f51; color: #fff; }
  .badge-visite { background: #2a9d8f; color: #fff; }
  .badge-overdue { background: #e63946; color: #fff; margin-left: 2px; }
  .badge-priorite { background: #6610f2; color: #fff; margin-left: 2px; }
  .so { color: var(--accent); font-size: .85rem; font-weight: 600; }
  .client { font-weight: 600; margin-top: .25rem; }
  .last-so { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: .72rem; font-weight: 600; margin-left: 6px; vertical-align: middle; }
  .last-so::before { content: "🛒 "; font-weight: 400; opacity: .8; }
  .last-so-fresh { background: #d3f9d8; color: #2b8a3e; }
  .last-so-mid { background: #fff3bf; color: #b08400; }
  .last-so-stale { background: #ffe0e0; color: #c92a2a; }
  .last-so-never { background: #e9ecef; color: #495057; }
  .addr { font-size: .85rem; color: #555; margin-top: .3rem; }
  .contact-badge { background: #e7f5ff; border-left: 4px solid #1971c2; padding: .35rem .7rem; margin: .35rem 0; font-size: .88rem; border-radius: 0 4px 4px 0; color: #1864ab; font-weight: 600; }
  .contact-badge::before { content: "👤 "; }
  .opnote { font-size: .84rem; color: #d9480f; background: #fff4e6; border-left: 4px solid #e8590c; padding: .3rem .6rem; margin: .25rem 0; border-radius: 0 4px 4px 0; }
  .field { font-size: .85rem; padding: .3rem .6rem; margin: .25rem 0; border-radius: 0 4px 4px 0; font-weight: 600; }
  .field .lbl { font-weight: 700; }
  .field-stock { background: #fff4e6; border-left: 4px solid #e8590c; color: #d9480f; }
  .field-stock::before { content: "📦 "; }
  .field-reassort { background: #f3f0ff; border-left: 4px solid #7048e8; color: #6741d9; }
  .field-reassort::before { content: "🔫 "; }
  .field-regle { background: #fff0f6; border-left: 4px solid #c2255c; color: #a61e4d; }
  .field-regle::before { content: "⚠️ "; }
  .route { margin-top: .35rem; font-size: .83rem; }
  .route a { color: var(--primary); font-weight: 600; text-decoration: none; }
  .route a::before { content: "🗺️ "; }
  .dayroute { background: #e9ecef; padding: .5rem 1rem; font-size: .83rem; margin-top: .3rem; border-radius: 6px; }
  .dayroute a { color: var(--primary); font-weight: 600; text-decoration: none; }
  @media(max-width:600px) { .visit-header { flex-direction: column; align-items: flex-start; } }"""


def build(weeks):
    nav = '<a class="week-btn" href="contacts.html">📇 Contacts &amp; délais</a>\n'
    for w in weeks:
        cls = "week-btn active" if w.get("active") else "week-btn"
        nav += f'  <a class="{cls}" href="#{w["id"]}" onclick="showWeek(\'{w["id"]}\')">{w["nav"]}</a>\n'
    body = "".join(week_html(w) for w in weeks)
    ids = [w["id"] for w in weeks]
    js = f"""<script>
var WEEKS = {ids};
function showWeek(id) {{
  WEEKS.forEach(function(w){{ var el=document.getElementById(w); if(el) el.style.display = (w===id)?'block':'none'; }});
  document.querySelectorAll('.week-nav a').forEach(function(a){{ a.classList.remove('active'); }});
  var btn = document.querySelector('.week-nav a[href="#'+id+'"]'); if(btn) btn.classList.add('active');
  if(history.replaceState) history.replaceState(null,'','#'+id);
}}
window.addEventListener('DOMContentLoaded', function(){{
  var h = location.hash.replace('#',''); if(WEEKS.indexOf(h)>=0) showWeek(h);
}});
</script>"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Planning Merchandiser — Teatower</title>
<style>
{CSS}
</style>
</head>
<body>
<h1>Planning Merchandiser — Teatower</h1>
<p class="subtitle">Merchandiser : Gilles · Base : Baillonville (5377) · Horaire : 08h30 – 17h00</p>
<div class="week-nav">
  {nav}</div>
{body}
{js}
</body>
</html>
"""


def check_pools_exclusifs(weeks):
    """GARDE-FOU pools exclusifs (REGLES §12) : aucun magasin merch ne doit etre
    dans le pool televente (Vanessa), SAUF les implantations (k='impl', toujours
    physiques). Extrait le #pid du nom de chaque stop et le compare au dernier
    televente_pool_*.csv. Affiche un WARNING bloquant a l'oeil."""
    import csv, re
    from glob import glob
    data_dir = OUT.resolve().parent.parent.parent / "Teatower" / "data"
    csvs = sorted(glob(str(data_dir / "televente_pool_*.csv")))
    if not csvs:
        print("[!] pas de televente_pool_*.csv -> garde-fou non applique")
        return
    tv = set()
    with open(csvs[-1], encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                tv.add(int(row["pid"]))
            except (KeyError, ValueError):
                pass
    pid_re = re.compile(r"#(\d+)")
    bad = []
    for w in weeks:
        for d in w["days"]:
            for s in d["stops"]:
                if s.get("k") == "impl":
                    continue  # implantation = toujours merch
                m = pid_re.search(s.get("n", ""))
                if m and int(m.group(1)) in tv:
                    bad.append(f"{w['id']}/{d['h']}: {s['n']}")
    if bad:
        print(f"[!!!] {len(bad)} magasin(s) MERCH presents dans le pool TELEVENTE "
              f"(a retirer -> Vanessa, REGLES §12) :")
        for b in bad:
            print(f"      - {b}")
    else:
        print(f"[OK] garde-fou pools exclusifs : aucun magasin merch en televente ({csvs[-1].split('/')[-1]})")


def main():
    from planning_data import WEEKS
    check_pools_exclusifs(WEEKS)
    html = build(WEEKS)
    OUT.write_text(html, encoding="utf-8")
    n = sum(len(d["stops"]) for w in WEEKS for d in w["days"])
    print(f"[+] {OUT} écrit — {len(WEEKS)} semaines, {n} stops")


if __name__ == "__main__":
    main()
