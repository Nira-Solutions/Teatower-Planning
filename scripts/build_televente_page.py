"""
build_televente_page.py — Page HTML du planning TELEVENTE (Vanessa), VUE HEBDO.

Lit le dernier televente_pool_*.csv (build_televente_pool.py) et genere la
semaine courante (Lun-Ven, ~9 appels/jour), recalee par les issues d'appel
saisies dans Odoo (tags [APPEL ... REFUS|NRP]) :
  - Commande passee (nouvelle SO dans la semaine) -> recale, sort de la file.
  - REFUS dans la semaine                         -> realise (remplace), sort.
  - NRP (injoignable) dans la semaine             -> reporte S+1 (reste du).
  - Reste du (next_call <= vendredi) et pas encore traite -> A APPELER.

Anti-rupture (overdue <= 90j) en jours ; win-back dormants (>90j) en annexe.
Aucune ecriture Odoo, aucun mail, aucun calendrier.

Sortie : OneDrive/Teatower-Planning/televente/index.html
"""

import csv
import html
from datetime import date, timedelta
from pathlib import Path

DATA = Path(r"C:\Users\FlowUP\OneDrive\Teatower\data")
OUT = Path(r"C:\Users\FlowUP\OneDrive\Teatower-Planning\televente\index.html")
DORMANT_THRESHOLD = 90
DAILY = 9
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
FERIES_BE = {  # jours feries Belgique (no call)
    date(2026, 1, 1), date(2026, 4, 6), date(2026, 5, 1), date(2026, 5, 14),
    date(2026, 5, 25), date(2026, 7, 21), date(2026, 8, 15), date(2026, 11, 1),
    date(2026, 11, 11), date(2026, 12, 25),
}

CSS = """
  :root { --primary:#7b2d6a; --accent:#b5179e; --warn:#e76f51; --bg:#f8f9fa; --card:#fff; --text:#212529; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); padding:1rem; max-width:900px; margin:0 auto; }
  h1 { color:var(--primary); font-size:1.5rem; margin-bottom:.3rem; }
  .subtitle { color:#666; font-size:.9rem; margin-bottom:1.2rem; }
  .summary { display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:.5rem; margin-bottom:1.2rem; }
  .summary-card { background:var(--primary); color:#fff; border-radius:8px; padding:.8rem; text-align:center; }
  .summary-card .num { font-size:1.7rem; font-weight:700; }
  .summary-card .label { font-size:.7rem; text-transform:uppercase; opacity:.85; }
  .alert { background:#fff3cd; border-left:4px solid var(--warn); padding:.6rem 1rem; margin-bottom:.8rem; border-radius:0 6px 6px 0; font-size:.85rem; }
  .alert strong { color:var(--warn); }
  .rules { background:#f3e8f1; border-left:4px solid var(--accent); padding:.6rem 1rem; margin-bottom:1rem; border-radius:0 6px 6px 0; font-size:.82rem; color:#6a1b5a; }
  .section-title { font-size:1.2rem; color:var(--primary); margin:1.6rem 0 .5rem; border-bottom:2px solid var(--accent); padding-bottom:.3rem; }
  .day { background:var(--card); border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,.1); margin-bottom:1rem; overflow:hidden; }
  .day-header { background:var(--primary); color:#fff; padding:.6rem 1rem; font-weight:600; display:flex; justify-content:space-between; align-items:center; }
  .day-header .cnt { font-weight:400; font-size:.85rem; opacity:.85; }
  .day-ferie { background:#495057; }
  .call { padding:.6rem 1rem; border-bottom:1px solid #eee; }
  .call:last-child { border-bottom:none; }
  .call-header { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:.3rem; }
  .rank { font-weight:700; color:var(--primary); }
  .client { font-weight:600; }
  .badge { display:inline-block; padding:2px 8px; border-radius:4px; font-size:.7rem; font-weight:600; text-transform:uppercase; margin-left:4px; }
  .badge-retard { background:#e63946; color:#fff; }
  .badge-bientot { background:#f4a261; color:#fff; }
  .badge-petit { background:#2a9d8f; color:#fff; }
  .badge-loin { background:#264653; color:#fff; }
  .badge-nrp { background:#6c757d; color:#fff; }
  .badge-ok { background:#2b8a3e; color:#fff; }
  .badge-refus { background:#a61e4d; color:#fff; }
  .meta { font-size:.82rem; color:#555; margin-top:.35rem; line-height:1.5; }
  .meta strong { color:var(--text); }
  .contact-badge { background:#fde7f5; border-left:4px solid var(--accent); padding:.35rem .7rem; margin:.35rem 0; font-size:.9rem; border-radius:0 4px 4px 0; color:#7b2d6a; font-weight:600; }
  .contact-badge::before { content:"\\1F4DE  "; }
  .refs { background:#eef6f5; padding:.35rem .6rem; margin-top:.35rem; font-size:.8rem; border-radius:4px; color:#1d6f63; }
  .refs::before { content:"\\1F4E6 Refs habituelles : "; font-weight:600; opacity:.8; }
  .recap { background:var(--card); border-radius:8px; padding:.5rem 1rem; margin-bottom:.5rem; font-size:.85rem; box-shadow:0 1px 2px rgba(0,0,0,.08); }
  @media(max-width:600px){ .call-header{ flex-direction:column; align-items:flex-start; } }
"""


def esc(s):
    return html.escape(str(s)) if s else ""


def pdate(s):
    return date.fromisoformat(s) if s else None


def maps_link(r):
    q = ", ".join(x for x in [r.get("street"), r.get("zip"), r.get("city")] if x)
    return "https://www.google.com/maps/search/?api=1&query=" + esc(q.replace(" ", "+"))


def render_call(r, rank):
    overdue = r["overdue_days"]
    if overdue > 0:
        badge = f'<span class="badge badge-retard">retard {overdue}j</span>'
    else:
        badge = f'<span class="badge badge-bientot">dû dans {-overdue}j</span>'
    motif = '<span class="badge badge-petit">petit assort.</span>' if "petit" in r["reason"] else ""
    if "eloigne" in r["reason"]:
        motif += f'<span class="badge badge-loin">{r["dist_km"]} km</span>'
    nrp_flag = '<span class="badge badge-nrp">déjà NRP</span>' if r.get("_nrp_prev") else ""

    tel = r["phone"] or r["mobile"] or ""
    if tel or r["email"]:
        contact = (f'<div class="contact-badge">{esc(tel)}'
                   + (f' &nbsp;|&nbsp; {esc(r["email"])}' if r["email"] else "") + "</div>")
    else:
        contact = '<div class="contact-badge" style="color:#c92a2a">☎️ TÉL MANQUANT — à compléter dans Odoo</div>'
    refs = f'<div class="refs">{esc(r["top_products"])}</div>' if r["top_products"] else ""
    adr = ", ".join(x for x in [r.get("street"), r.get("zip"), r.get("city")] if x)
    return f"""
  <div class="call">
    <div class="call-header">
      <span><span class="rank">{rank}.</span> <span class="client">{esc(r['magasin'])}</span> <span style="color:#999;font-size:.78rem">#{r['pid']}</span></span>
      <span>{badge}{motif}{nrp_flag}</span>
    </div>
    {contact}
    <div class="meta">
      📍 <a href="{maps_link(r)}" target="_blank">{esc(adr)}</a> &nbsp;·&nbsp; {esc(r['dist_km'])} km<br>
      🛒 Dernière cmd : <strong>{esc(r['last_order'])}</strong> ({r['days_since']}j) &nbsp;·&nbsp;
      cadence cible : <strong>{r['target_interval']}j</strong> &nbsp;·&nbsp; {esc(r['n_refs'])} réfs &nbsp;·&nbsp; CA {esc(r['avg_mois'])}€/mois
    </div>
    {refs}
  </div>"""


def main():
    cands = sorted(DATA.glob("televente_pool_*.csv"))
    csv_path = cands[-1]
    stamp = csv_path.stem.replace("televente_pool_", "")
    today = date.fromisoformat(stamp)
    mon = today - timedelta(days=today.weekday())
    fri = mon + timedelta(days=4)
    iso_week = today.isocalendar()[1]
    in_week = lambda d: d is not None and mon <= d <= fri

    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    for r in rows:
        r["overdue_days"] = int(r["overdue_days"])
        r["_next"] = pdate(r["next_call"])
        r["_lo"] = pdate(r["last_order"])
        r["_refus"] = pdate(r.get("last_refus"))
        r["_nrp"] = pdate(r.get("last_nrp"))

    # statuts de la semaine
    commande_wk = [r for r in rows if in_week(r["_lo"])]
    refus_wk = [r for r in rows if in_week(r["_refus"])]
    nrp_wk = [r for r in rows if in_week(r["_nrp"])]
    handled = {id(r) for r in commande_wk + refus_wk}
    nrp_ids = {id(r) for r in nrp_wk}

    # dus cette semaine, non traites
    due = [r for r in rows if r["_next"] and r["_next"] <= fri
           and id(r) not in handled and id(r) not in nrp_ids]
    anti = sorted([r for r in due if r["overdue_days"] <= DORMANT_THRESHOLD],
                  key=lambda r: (-r["overdue_days"], -int(r["avg_mois"])))
    winback = sorted([r for r in due if r["overdue_days"] > DORMANT_THRESHOLD],
                     key=lambda r: (-r["overdue_days"], -int(r["avg_mois"])))
    # marquer ceux deja NRP une fois (semaine precedente) pour info
    for r in anti:
        r["_nrp_prev"] = r["_nrp"] is not None

    # repartition en jours ouvres non feries
    work_days = [(JOURS[i], mon + timedelta(days=i)) for i in range(5)]
    open_days = [(n, d) for n, d in work_days if d not in FERIES_BE]
    queue = list(anti)
    day_slots = []  # (jour, date, [calls], ferie?)
    for n, d in work_days:
        if d in FERIES_BE:
            day_slots.append((n, d, [], True))
        else:
            chunk = queue[:DAILY]
            queue = queue[DAILY:]
            day_slots.append((n, d, chunk, False))
    overflow = queue  # ne rentre pas dans la semaine

    parts = [f"""<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Planning Télévente — Teatower</title>
<style>{CSS}</style></head><body>
<h1>Planning Télévente — Teatower</h1>
<p class="subtitle">Télévendeuse : Vanessa &nbsp;|&nbsp; Semaine S{iso_week} ({mon.strftime('%d/%m')}–{fri.strftime('%d/%m')}) &nbsp;|&nbsp; ~{DAILY} appels/jour &nbsp;|&nbsp; généré le {stamp}</p>

<div class="summary">
  <div class="summary-card"><div class="num">{len(anti)}</div><div class="label">À appeler</div></div>
  <div class="summary-card"><div class="num">{len(commande_wk)}</div><div class="label">Commandé S{iso_week}</div></div>
  <div class="summary-card"><div class="num">{len(refus_wk)}</div><div class="label">Refus S{iso_week}</div></div>
  <div class="summary-card"><div class="num">{len(nrp_wk)}</div><div class="label">↪ Reportés S+1</div></div>
  <div class="summary-card"><div class="num">{len(winback)}</div><div class="label">Win-back dispo</div></div>
</div>

<div class="rules">
  <strong>Issues d'appel — à saisir dans la fiche Odoo du magasin :</strong><br>
  ✅ Commande → encoder la SO (recale tout seul).&nbsp;
  ❌ Refus → tag <code>[APPEL {today} REFUS]</code> (sort de la semaine, revient à +cadence).&nbsp;
  ☎️ Injoignable → tag <code>[APPEL {today} NRP]</code> (reporté S+1, reste dû).<br>
  Segment : réfs ≤ 10 OU (dist &gt; 60 km ET réfs &lt; 20). Cadence ×0,75 clamp [14,35]j. Pas de mail/calendrier auto.
</div>
"""]

    parts.append(f'<h2 class="section-title">📞 Semaine S{iso_week} — anti-rupture ({len(anti)} appels)</h2>')
    if not anti:
        parts.append('<div class="alert">Aucun magasin dû cette semaine. File à jour 🎉 — piocher dans le win-back ci-dessous.</div>')
    for n, d, chunk, ferie in day_slots:
        if ferie:
            parts.append(f'<div class="day"><div class="day-header day-ferie">{n} {d.strftime("%d/%m")} '
                         f'<span class="cnt">🚫 JOUR FÉRIÉ — pas d\'appels</span></div></div>')
            continue
        hdr = f'<div class="day"><div class="day-header">{n} {d.strftime("%d/%m")} <span class="cnt">{len(chunk)} appels</span></div>'
        parts.append(hdr)
        if not chunk:
            parts.append('<div class="call" style="color:#888">— rien à appeler ce jour —</div>')
        for i, r in enumerate(chunk, 1):
            parts.append(render_call(r, i))
        parts.append('</div>')

    if overflow:
        parts.append(f'<div class="alert"><strong>{len(overflow)} appels au-delà de la capacité S{iso_week}</strong> '
                     f'(report S+1 automatique) : ' + ", ".join(esc(r["magasin"]) for r in overflow[:15]) + '.</div>')

    # reportes S+1 (NRP cette semaine)
    if nrp_wk:
        parts.append(f'<h2 class="section-title">☎️ Injoignables — reportés S+1 ({len(nrp_wk)})</h2>')
        parts.append('<div class="alert">Tentés cette semaine sans réponse. Reviennent automatiquement la semaine prochaine.</div>')
        for r in sorted(nrp_wk, key=lambda r: -r["overdue_days"]):
            parts.append(f'<div class="recap"><span class="badge badge-nrp">NRP {r["_nrp"]}</span> '
                         f'<strong>{esc(r["magasin"])}</strong> #{r["pid"]} — {r["phone"] or r["mobile"] or "tél?"}</div>')

    # realise cette semaine
    if commande_wk or refus_wk:
        parts.append(f'<h2 class="section-title">✔️ Réalisé cette semaine ({len(commande_wk)+len(refus_wk)})</h2>')
        for r in commande_wk:
            parts.append(f'<div class="recap"><span class="badge badge-ok">commandé {r["_lo"]}</span> '
                         f'<strong>{esc(r["magasin"])}</strong> #{r["pid"]}</div>')
        for r in refus_wk:
            parts.append(f'<div class="recap"><span class="badge badge-refus">refus {r["_refus"]}</span> '
                         f'<strong>{esc(r["magasin"])}</strong> #{r["pid"]} — recontact ~{r["target_interval"]}j</div>')

    # win-back
    if winback:
        parts.append(f'<h2 class="section-title">🔄 Win-back — dormants &gt;90j ({len(winback)})</h2>')
        parts.append('<div class="alert">Clients perdus de vue. Discours réactivation. À traiter quand la semaine est creuse.</div>')
        for i, r in enumerate(winback, 1):
            parts.append(render_call(r, i))

    parts.append("\n</body></html>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(parts), encoding="utf-8")
    cap = len(open_days) * DAILY
    print(f"[+] Page S{iso_week} : {OUT}")
    print(f"    A appeler {len(anti)} (cap {cap}) | commande {len(commande_wk)} | refus {len(refus_wk)} | "
          f"NRP {len(nrp_wk)} | winback {len(winback)} | overflow {len(overflow)}")


if __name__ == "__main__":
    main()
