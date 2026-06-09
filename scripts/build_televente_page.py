"""
build_televente_page.py — Genere la page HTML du planning TELEVENTE (Vanessa)
a partir du dernier televente_pool_YYYY-MM-DD.csv produit par build_televente_pool.py.

Sortie : OneDrive/Teatower-Planning/televente/index.html
  -> publie sur https://nira-solutions.github.io/Teatower-Planning/televente/

Deux files :
  - "Anti-rupture" : overdue_days <= 90, triees par retard decroissant.
    Le LOT DU JOUR = les 9 premieres (capacite Vanessa = ~9 appels/jour).
  - "Win-back dormants" : overdue_days > 90 (comptes a reactiver).

Aucun ecriture Odoo, aucun mail, aucun calendrier.
"""

import csv
import html
from datetime import date
from pathlib import Path

DATA = Path(r"C:\Users\FlowUP\OneDrive\Teatower\data")
OUT = Path(r"C:\Users\FlowUP\OneDrive\Teatower-Planning\televente\index.html")
DORMANT_THRESHOLD = 90  # overdue_days > 90 -> win-back
DAILY = 9               # capacite Vanessa

CSS = """
  :root { --primary:#7b2d6a; --accent:#b5179e; --warn:#e76f51; --bg:#f8f9fa; --card:#fff; --text:#212529; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); padding:1rem; max-width:900px; margin:0 auto; }
  h1 { color:var(--primary); font-size:1.5rem; margin-bottom:.3rem; }
  .subtitle { color:#666; font-size:.9rem; margin-bottom:1.2rem; }
  .summary { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:.5rem; margin-bottom:1.2rem; }
  .summary-card { background:var(--primary); color:#fff; border-radius:8px; padding:.8rem; text-align:center; }
  .summary-card .num { font-size:1.8rem; font-weight:700; }
  .summary-card .label { font-size:.72rem; text-transform:uppercase; opacity:.85; }
  .alert { background:#fff3cd; border-left:4px solid var(--warn); padding:.6rem 1rem; margin-bottom:.8rem; border-radius:0 6px 6px 0; font-size:.85rem; }
  .alert strong { color:var(--warn); }
  .rules { background:#f3e8f1; border-left:4px solid var(--accent); padding:.6rem 1rem; margin-bottom:1rem; border-radius:0 6px 6px 0; font-size:.82rem; color:#6a1b5a; }
  .section-title { font-size:1.2rem; color:var(--primary); margin:1.6rem 0 .5rem; border-bottom:2px solid var(--accent); padding-bottom:.3rem; }
  .call { background:var(--card); border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,.1); margin-bottom:.7rem; padding:.7rem 1rem; border-left:4px solid #ddd; }
  .call.today { border-left:4px solid var(--accent); background:#fdf5fb; }
  .call.dormant { border-left:4px solid #e63946; }
  .call-header { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:.3rem; }
  .rank { font-weight:700; color:var(--primary); min-width:2rem; }
  .client { font-weight:600; }
  .badge { display:inline-block; padding:2px 8px; border-radius:4px; font-size:.7rem; font-weight:600; text-transform:uppercase; margin-left:4px; }
  .badge-retard { background:#e63946; color:#fff; }
  .badge-bientot { background:#f4a261; color:#fff; }
  .badge-ok { background:#adb5bd; color:#fff; }
  .badge-petit { background:#2a9d8f; color:#fff; }
  .badge-loin { background:#264653; color:#fff; }
  .badge-today { background:var(--accent); color:#fff; }
  .meta { font-size:.82rem; color:#555; margin-top:.35rem; line-height:1.5; }
  .meta strong { color:var(--text); }
  .contact-badge { background:#fde7f5; border-left:4px solid var(--accent); padding:.35rem .7rem; margin:.35rem 0; font-size:.9rem; border-radius:0 4px 4px 0; color:#7b2d6a; font-weight:600; }
  .contact-badge::before { content:"\\1F4DE  "; }
  .refs { background:#eef6f5; padding:.35rem .6rem; margin-top:.35rem; font-size:.8rem; border-radius:4px; color:#1d6f63; }
  .refs::before { content:"\\1F4E6 Refs habituelles : "; font-weight:600; opacity:.8; }
  .notes { font-size:.78rem; color:#777; margin-top:.3rem; font-style:italic; }
  @media(max-width:600px){ .call-header{ flex-direction:column; align-items:flex-start; } }
"""


def esc(s):
    return html.escape(str(s)) if s else ""


def tel_of(r):
    return r["phone"] or r["mobile"] or ""


def maps_link(r):
    q = ", ".join(x for x in [r.get("street"), r.get("zip"), r.get("city")] if x)
    return "https://www.google.com/maps/search/?api=1&query=" + esc(q.replace(" ", "+"))


def render_call(r, rank, is_today=False, is_dormant=False):
    overdue = int(r["overdue_days"])
    if overdue > 0:
        badge = f'<span class="badge badge-retard">retard {overdue}j</span>'
    elif overdue >= -7:
        badge = f'<span class="badge badge-bientot">dû dans {-overdue}j</span>'
    else:
        badge = f'<span class="badge badge-ok">échéance {-overdue}j</span>'
    motif = ('<span class="badge badge-petit">petit assort.</span>'
             if "petit" in r["reason"] else "")
    if "eloigne" in r["reason"] or "loin" in r["reason"]:
        motif += f'<span class="badge badge-loin">{r["dist_km"]} km</span>'
    today_badge = '<span class="badge badge-today">lot du jour</span>' if is_today else ""

    cls = "call"
    if is_today:
        cls += " today"
    if is_dormant:
        cls += " dormant"

    tel = tel_of(r)
    contact = (f'<div class="contact-badge">{esc(tel)}'
               + (f' &nbsp;|&nbsp; {esc(r["email"])}' if r["email"] else "")
               + "</div>") if (tel or r["email"]) else \
              '<div class="contact-badge" style="color:#c92a2a">☎️ TÉL MANQUANT — à compléter dans Odoo</div>'

    refs = f'<div class="refs">{esc(r["top_products"])}</div>' if r["top_products"] else ""
    notes = f'<div class="notes">{esc(r["notes"])}</div>' if r.get("notes") else ""

    adr = ", ".join(x for x in [r.get("street"), r.get("zip"), r.get("city")] if x)
    return f"""
<div class="{cls}">
  <div class="call-header">
    <span><span class="rank">{rank}</span> <span class="client">{esc(r['magasin'])}</span> <span style="color:#999;font-size:.8rem">#{r['pid']}</span></span>
    <span>{today_badge}{badge}{motif}</span>
  </div>
  {contact}
  <div class="meta">
    📍 <a href="{maps_link(r)}" target="_blank">{esc(adr)}</a> &nbsp;·&nbsp; {esc(r['dist_km'])} km<br>
    🛒 Dernière cmd : <strong>{esc(r['last_order'])}</strong> ({r['days_since']}j) &nbsp;·&nbsp;
    cadence cible : <strong>{r['target_interval']}j</strong> &nbsp;·&nbsp;
    {esc(r['n_refs'])} réfs &nbsp;·&nbsp; CA {esc(r['avg_mois'])}€/mois
  </div>
  {refs}
  {notes}
</div>"""


def main():
    stamp = date.today().isoformat()
    csv_path = DATA / f"televente_pool_{stamp}.csv"
    if not csv_path.exists():
        cands = sorted(DATA.glob("televente_pool_*.csv"))
        csv_path = cands[-1]
        stamp = csv_path.stem.replace("televente_pool_", "")
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))

    for r in rows:
        r["overdue_days"] = int(r["overdue_days"])
    anti = [r for r in rows if r["overdue_days"] <= DORMANT_THRESHOLD]
    dorm = [r for r in rows if r["overdue_days"] > DORMANT_THRESHOLD]
    anti.sort(key=lambda r: (-r["overdue_days"], -int(r["avg_mois"])))
    dorm.sort(key=lambda r: (-r["overdue_days"], -int(r["avg_mois"])))

    ca_total = sum(int(r["revenue_12m"]) for r in rows)
    en_retard = sum(1 for r in anti if r["overdue_days"] > 0)

    parts = []
    parts.append(f"""<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Planning Télévente — Teatower</title>
<style>{CSS}</style></head><body>
<h1>Planning Télévente — Teatower</h1>
<p class="subtitle">Télévendeuse : Vanessa &nbsp;|&nbsp; Cible : GMS petit assortiment ou éloignés &nbsp;|&nbsp; Capacité ~{DAILY} appels/jour &nbsp;|&nbsp; Généré le {stamp}</p>

<div class="summary">
  <div class="summary-card"><div class="num">{len(rows)}</div><div class="label">Pool Vanessa</div></div>
  <div class="summary-card"><div class="num">{en_retard}</div><div class="label">En retard</div></div>
  <div class="summary-card"><div class="num">{len(dorm)}</div><div class="label">Dormants win-back</div></div>
  <div class="summary-card"><div class="num">{ca_total:,}€</div><div class="label">CA pool 12m</div></div>
</div>

<div class="rules">
  <strong>Règles du pool</strong> (Nicolas 09/06/2026) — segment exclusif du merch Gilles.<br>
  Vanessa = réfs ≤ 10 <em>OU</em> (distance &gt; 60 km <em>ET</em> réfs &lt; 20). Gros comptes éloignés (≥ 20 réfs) → restent à Gilles.<br>
  Cadence : intervalle historique × 0,75, plancher 14j / plafond 35j (l'historique sous-estime le besoin réel à cause des appels oubliés).<br>
  <em>Pas de mail ni de calendrier automatique. La prise de commande met à jour Odoo → le magasin redescend dans la file.</em>
</div>

<div class="alert"><strong>Lot du jour :</strong> les <strong>{DAILY} premiers</strong> de la file Anti-rupture (surlignés). Une fois la commande passée dans Odoo, le magasin sort automatiquement du haut de file au prochain rafraîchissement.</div>

<h2 class="section-title">📞 File Anti-rupture ({len(anti)})</h2>
""")
    for i, r in enumerate(anti, 1):
        parts.append(render_call(r, i, is_today=(i <= DAILY)))

    parts.append(f'\n<h2 class="section-title">🔄 Win-back — comptes dormants &gt;90j ({len(dorm)})</h2>\n')
    parts.append('<div class="alert">Clients perdus de vue (souvent les "oublis"). Discours réactivation, pas anti-rupture. À traiter quand la file principale est creuse.</div>\n')
    for i, r in enumerate(dorm, 1):
        parts.append(render_call(r, i, is_dormant=True))

    parts.append("\n</body></html>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"[+] Page : {OUT}")
    print(f"    Anti-rupture {len(anti)} (en retard {en_retard}) | Dormants {len(dorm)} | CA {ca_total}€")


if __name__ == "__main__":
    main()
