"""
build_agents_page.py — Rend la page "Agents Teatower — etat & evolution".

Remplace `agents_dashboard.html` (16/04/2026), dont le roster etait fige a 12
agents et dont les niveaux venaient d'une file simulee (`data/nira_queue.json`,
gelee au 06/07/2026).

Ici tout vient de deux sources reelles :
  - `git log` du depot Teatower-Planning  -> missions livrees, attribuees a un
    agent par mots-cles de domaine (heuristique, assumee et signalee sur la page)
  - `git log -- .claude/agents/`          -> naissance et refontes de chaque
    agent, plus le roster courant lu sur disque

Reprend le langage visuel des dashboards B2B (`b2b_style` / `b2b_render`).

Sortie : `agents/index.html`
         -> https://nira-solutions.github.io/Teatower-Planning/agents/

Usage : python reports/build_agents_page.py
"""
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from b2b_render import card, esc, kpi, note, section, trunc  # noqa: E402
from b2b_style import CSS, CSS_WEEKLY  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SINCE = "2026-01-01"
TODAY = date.today()

# --------------------------------------------------------------------------
# Roster — un agent = un fichier .claude/agents/*.md (ou une skill .claude/)
# `kw` : mots-cles de domaine, testes sur le sujet de commit normalise (sans
# accents, minuscules). Le premier agent qui matche prend la mission, d'ou
# l'ordre : du plus specifique au plus generique.
# --------------------------------------------------------------------------
AGENTS = [
    {"key": "compta", "name": "Compta", "role": "Comptable senior — factures, lettrage, Peppol, cloture",
     "kind": "agent", "emoji": "\U0001f4b6", "kw": [
         "compta", "factur", "lettrage", "peppol", "tva", "bilan", "balance agee",
         "amort", "salaire", "accise", "echeanc", "impay", "relance client",
         "relance pro", "honoraires", "cloture", "affacturage", "ing", "bnp",
         "p&l", "provision", "ag speciale", "banque"]},
    {"key": "planning", "name": "Planning", "role": "Tournees merch Gilles + televente Vanessa",
     "kind": "skill", "skill": ".claude/commands/planning-teatower.md",
     "emoji": "\U0001f5fa", "kw": [
         "planning", "tournee", "televente", "visite", "merch", "implantation",
         "no-merch", "queue s", "s19 queue", "terrain"]},
    {"key": "stock-manager", "name": "Stock Manager", "role": "Reappro multi-depots, orderpoints, inventaires",
     "kind": "skill", "skill": ".claude/commands/stock-manager.md",
     "emoji": "\U0001f4e6", "kw": [
         "stock", "reappro", "orderpoint", "inventaire", "rupture", "picking",
         "depot", "camionnette", "sendcloud", "livraison"]},
    {"key": "purchase", "name": "Purchase", "role": "Achats & sourcing — PO Kirchner, prix/delais fournisseurs",
     "kind": "agent", "emoji": "\U0001f6d2", "kw": [
         "purchase", "achat", "kirchner", "fournisseur", "rfq", "lead time",
         "po ", "appro", "commande fournisseur"]},
    {"key": "support-order", "name": "Support Order", "role": "ADV B2B/GMS — bons de commande -> devis Odoo",
     "kind": "agent", "emoji": "\U0001f4dd", "kw": [
         "bon de commande", "devis", "commande client", "support", "adv",
         "s05", "s06", "upload commande"]},
    {"key": "odoo", "name": "Odoo IT", "role": "Expert Odoo 18 — flux, crons, routes, XML-RPC",
     "kind": "agent", "emoji": "\U0001f9d9", "kw": [
         "odoo", "cron", "xml-rpc", "route", "module", "champ custom",
         "automation", "devmode", "sequence", "pos ", "flux"]},
    {"key": "seo-shopify", "name": "SEO Shopify", "role": "Fiches produit Shopify — copy, meta, multilingue",
     "kind": "agent", "emoji": "\U0001f50e", "kw": [
         "shopify", "seo", "fiche produit", "meta title", "meta description",
         "handle", "traduction fiche"]},
    {"key": "packaging", "name": "Packaging & Brand", "role": "Packaging, identite, planogrammes & PLV",
     "kind": "agent", "emoji": "\U0001f381", "kw": [
         "packaging", "imprimeur", "pantone", "etiquette", "display", "plv",
         "planogramme", "coffret", "avent", "vitrine", "doypack", "bat ",
         "plateforme de marque", "identite", "boite metal"]},
    {"key": "product-data", "name": "Product Data", "role": "Catalogue Odoo — SKU, descriptions, visuels",
     "kind": "agent", "emoji": "\U0001f9fe", "kw": [
         "product", "produit", "catalogue", "sku", "photo", "gamme",
         "nomenclature produit", "hausse tarifaire", "liste de prix", "tarif"]},
    {"key": "production", "name": "Production", "role": "Ordres de fabrication, BoM, assemblage",
     "kind": "agent", "emoji": "\U0001f3ed", "kw": [
         "production", "bom", "mrp", "assortiment", "assemblage", "vrac",
         "sachet", "co-packer", "saupont"]},
    {"key": "marketing", "name": "Marketing", "role": "Shopify 360, Amazon, newsletters, campagnes",
     "kind": "agent", "emoji": "✨", "kw": [
         "marketing", "newsletter", "campagne", "amazon", "fba", "promo",
         "mailchimp", "salon", "b2c", "reduction", "code bnp", "sondage"]},
    {"key": "sales-crm", "name": "Sales-CRM", "role": "Pipeline Jerome, leads, prospection, commissions",
     "kind": "agent", "emoji": "\U0001f91d", "kw": [
         "crm", "lead", "commission", "prospect", "sales", "opportunite",
         "carrefour", "delhaize", "intermarche", "spar", "gms", "client",
         "offre", "woyaffe", "awex", "jerome"]},
    {"key": "data-bi", "name": "Data-BI", "role": "KPI, dashboards, forecast, business reviews",
     "kind": "agent", "emoji": "\U0001f52e", "kw": [
         "dashboard", "data", "kpi", "forecast", "rentabilite", "analyse",
         "cockpit", "board", "weekly", "rapport", "portefeuille", "segment",
         "b2b dashboard", "saisonnalite", "capex", "audit"]},
    {"key": "upload-merch", "name": "Upload Merchandiser", "role": "Retours terrain Gilles -> Odoo (photos, notes)",
     "kind": "skill", "skill": ".claude/commands/upload-merchandiser.md",
     "emoji": "\U0001f4f8", "kw": ["upload merch", "retour terrain", "photos terrain"]},
]

NIRA = {"key": "nira", "name": "Nira", "role": "Agent principal — orchestrateur, copie numerique de Nicolas"}

# Bruit de depot : ni mission, ni agent.
NOISE = ("merge branch", "merge remote", "queue: done", "wip", "gitignore",
         "readme", "initial commit", "florine", "creds:", "dashboard agents",
         "agents_dashboard")


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def git(*args):
    out = subprocess.run(["git", "-C", str(ROOT), *args],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace")
    return out.stdout.splitlines()


# --------------------------------------------------------------------------
# 1. Missions = commits, attribuees par domaine
# --------------------------------------------------------------------------
RE_QUEUE = re.compile(r"^queue:\s*([a-z-]+)\s+start\s*[—-]+\s*(.*)$", re.I)

# Les mots-cles matchent en DEBUT de mot, suffixe libre : "accise" attrape
# "accises", "factur" attrape "facturation". La frontiere gauche est
# obligatoire — sans elle "ing" (la banque) se declenche sur "planning" et vole
# toutes ses missions au bon agent. EXACT = les sigles courts, ou un suffixe
# libre ferait n'importe quoi ("pos" -> "postee", "bat" -> "batiment").
EXACT = {"ing", "pos", "bat", "data", "po", "bom", "crm", "gms", "tva", "sku"}
KW_RE = {a["key"]: [re.compile(r"(?<![a-z0-9])" + re.escape(k)
                              + (r"(?![a-z0-9])" if k in EXACT else r"[a-z]*"))
                    for k in a["kw"]] for a in AGENTS}


def attribute(subject):
    """(agent_key, titre nettoye) ou (None, _) si non attribuable."""
    n = norm(subject)
    if any(n.startswith(x) or x in n[:24] for x in NOISE):
        return None, subject
    # Les commits "Queue: <agent> start — tache" portent l'agent en clair :
    # attribution certaine, elle prime sur les mots-cles.
    m = RE_QUEUE.match(subject)
    if m:
        key = m.group(1).lower()
        key = {"merchandiser": "upload-merch"}.get(key, key)
        if any(a["key"] == key for a in AGENTS):
            return key, m.group(2).strip()
    for a in AGENTS:
        if any(rx.search(n) for rx in KW_RE[a["key"]]):
            return a["key"], subject
    return None, subject


missions = defaultdict(list)      # key -> [(date, titre)]
per_month_total = defaultdict(int)
unmatched = []

for line in git("log", f"--since={SINCE}", "--date=short",
                "--pretty=format:%ad|%s"):
    if "|" not in line:
        continue
    d, subj = line.split("|", 1)
    key, title = attribute(subj)
    if key is None:
        if not any(x in norm(subj) for x in NOISE):
            unmatched.append((d, subj))
        continue
    missions[key].append((d, title))
    per_month_total[d[:7]] += 1

MONTHS = sorted({d[:7] for lst in missions.values() for d, _ in lst})
MONTH_LABEL = {"01": "jan", "02": "fev", "03": "mar", "04": "avr", "05": "mai",
               "06": "juin", "07": "juil", "08": "aout", "09": "sep",
               "10": "oct", "11": "nov", "12": "dec"}


FIRST_LABEL = ""  # rempli apres mlabel


def mlabel(ym):
    return MONTH_LABEL[ym[5:7]]


# --------------------------------------------------------------------------
FIRST_LABEL = f"{mlabel(MONTHS[0])}. {MONTHS[0][:4]}"

# --------------------------------------------------------------------------
# 2. Naissance / refontes des agents (git log sur .claude/agents)
# --------------------------------------------------------------------------
births = {}       # key -> date de creation
lifecycle = []    # (date, sujet, [keys touches])
cur = None
for line in git("log", "--date=short", "--reverse",
                "--pretty=format:@@%ad|%s", "--name-status", "--", ".claude"):
    if line.startswith("@@"):
        d, subj = line[2:].split("|", 1)
        cur = {"date": d, "subject": subj, "keys": [], "new": []}
        lifecycle.append(cur)
    elif line and cur and line[0] in "AM":
        status, path = line.split("\t", 1)
        stem = Path(path).stem
        key = {"upload-merchandiser": "upload-merch",
               "planning-teatower": "planning"}.get(stem, stem)
        if key not in cur["keys"]:
            cur["keys"].append(key)
        if status == "A" and key not in births:
            births[key] = d
            cur["new"].append(key)

# Fichiers presents mais jamais commites (skills locales) : date de fichier.
for a in AGENTS:
    if a["key"] in births:
        continue
    p = ROOT / a.get("skill", f".claude/agents/{a['key']}.md")
    if p.exists():
        births[a["key"]] = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")

last_edit = {}
for a in AGENTS + [NIRA]:
    p = ROOT / a.get("skill", f".claude/agents/{a['key']}.md")
    if p.exists():
        last_edit[a["key"]] = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")

lifecycle = [e for e in lifecycle if e["keys"]]


# --------------------------------------------------------------------------
# 3. Rendu
# --------------------------------------------------------------------------
RE_MONEY = re.compile(r"\d[\d.\s]*,\d{2}\s*(?:EUR|€)|\d[\d.\s]*\s*(?:EUR|€)")


def hide_money(s):
    """La page est servie sur un depot PUBLIC : les titres de mission restent,
    les montants partent. Un lettrage bancaire au centime n'a rien a faire en
    ligne, et le titre reste lisible sans lui."""
    return RE_MONEY.sub("… EUR", s)


def fr(d):
    return f"{d[8:10]}/{d[5:7]}/{d[2:4]}"


def days_since(d):
    return (TODAY - date.fromisoformat(d)).days


def sparkline(counts, width=132, height=30):
    """Barres mensuelles — l'evolution, pas le total."""
    top = max(counts) if counts and max(counts) else 1
    n = len(counts) or 1
    bw = width / n
    bars = []
    for i, c in enumerate(counts):
        h = max(2, round(c / top * (height - 4)))
        x = round(i * bw, 1)
        y = height - h
        last = i == n - 1
        fill = "var(--accent)" if last else "#cbd5cb"
        bars.append(f'<rect x="{x}" y="{y}" width="{round(bw - 3, 1)}" '
                    f'height="{h}" rx="1.5" fill="{fill}"/>')
    return (f'<svg class="spark" viewBox="0 0 {width} {height}" width="{width}" '
            f'height="{height}" role="img" aria-hidden="true">{"".join(bars)}</svg>')


def status_pill(key, total, last_d):
    if total == 0:
        return '<span class="pill">jamais sollicite</span>'
    dd = days_since(last_d)
    born = births.get(key)
    if born and days_since(born) <= 60:
        return '<span class="pill new">nouveau</span>'
    if dd <= 14:
        return '<span class="pill new">actif</span>'
    if dd <= 45:
        return '<span class="pill back">au ralenti</span>'
    return '<span class="pill risk">dormant</span>'


rows = []
for a in AGENTS:
    lst = sorted(missions.get(a["key"], []), reverse=True)
    counts = [sum(1 for d, _ in lst if d[:7] == m) for m in MONTHS]
    last30 = sum(1 for d, _ in lst if days_since(d) <= 30)
    rows.append({**a, "missions": lst, "counts": counts, "total": len(lst),
                 "last30": last30, "last": lst[0][0] if lst else None})

rows.sort(key=lambda r: (-r["last30"], -r["total"]))

cards = []
for r in rows:
    born = births.get(r["key"])
    edited = last_edit.get(r["key"])
    recent = "".join(
        f'<li><span class="mono">{fr(d)}</span> {esc(trunc(hide_money(t), 62))}</li>'
        for d, t in r["missions"][:3]) or '<li class="muted">aucune mission tracee</li>'
    kind = ("skill <code>/" + Path(r["skill"]).stem + "</code>") if r["kind"] == "skill" \
        else "sous-agent"
    cards.append(f"""
  <div class="ag">
    <div class="ag-head">
      <span class="ag-emoji">{r['emoji']}</span>
      <div class="ag-id">
        <h3>{esc(r['name'])}</h3>
        <div class="ag-role">{esc(r['role'])}</div>
      </div>
      {status_pill(r['key'], r['total'], r['last']) }
    </div>
    <div class="ag-nums">
      <div><b>{r['total']}</b><span>missions depuis {FIRST_LABEL}</span></div>
      <div><b>{r['last30']}</b><span>sur 30 jours</span></div>
      <div class="ag-spark">{sparkline(r['counts'])}
        <span>{mlabel(MONTHS[0])} &rarr; {mlabel(MONTHS[-1])}</span></div>
    </div>
    <ul class="ag-recent">{recent}</ul>
    <div class="ag-foot">
      {kind} &middot; ne le {fr(born) if born else '?'}
      &middot; prompt revu le {fr(edited) if edited else '?'}
    </div>
  </div>""")

# Frise de vie de la flotte — les naissances, plus les 4 dernieres retouches :
# la liste complete des refontes de prompt n'apprend rien a personne.
keep = [e for e in lifecycle if e["new"]] + [e for e in lifecycle if not e["new"]][-4:]
keep.sort(key=lambda e: e["date"])

tl = []
for e in keep:
    names = {a["key"]: a["name"] for a in AGENTS}
    names[NIRA["key"]] = NIRA["name"]
    created = [names.get(k, k) for k in e["new"]]
    touched = [names.get(k, k) for k in e["keys"] if k not in e["new"]]
    what = ""
    if created:
        what += f'<b>+ {", ".join(created)}</b>'
    if touched:
        what += ("<span class=\"muted\"> &middot; refonte "
                 + ", ".join(touched) + "</span>")
    tl.append(f'<li><span class="mono">{fr(e["date"])}</span> {what or ""}'
              f'<div class="tl-sub">{esc(e["subject"])}</div></li>')

# Volume mensuel toutes missions confondues
vol_top = max(per_month_total.values()) if per_month_total else 1
vol = "".join(
    f'<div class="hour-bar"><span class="hour-label">{mlabel(m)}</span>'
    f'<div class="bar-track"><div class="bar" style="width:'
    f'{round(per_month_total[m] / vol_top * 100)}%"><span class="c1" '
    f'style="width:100%"></span></div></div>'
    f'<span class="bar-value">{per_month_total[m]}</span></div>'
    for m in MONTHS)

total_missions = sum(r["total"] for r in rows)
actifs = sum(1 for r in rows if r["last30"] > 0)
top = rows[0]
newest = max(births.items(), key=lambda kv: kv[1])
newest_name = next((a["name"] for a in AGENTS if a["key"] == newest[0]), newest[0])

EXTRA = """
  .ag-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .ag { background: var(--card); border: 1px solid var(--border); border-radius: 10px;
        padding: 16px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
  .ag-head { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
  .ag-emoji { font-size: 22px; line-height: 1; }
  .ag-id { flex: 1; min-width: 0; }
  .ag-id h3 { font-size: 15px; font-weight: 700; }
  .ag-role { font-size: 12px; color: var(--muted); }
  .ag-nums { display: flex; align-items: flex-end; gap: 18px;
             padding: 10px 0 12px; border-top: 1px solid var(--border); }
  .ag-nums > div { display: flex; flex-direction: column; }
  .ag-nums b { font-size: 20px; font-weight: 700; color: var(--accent); line-height: 1.1; }
  .ag-nums span { font-size: 10px; color: var(--muted); text-transform: uppercase;
                  letter-spacing: 0.3px; }
  .ag-spark { margin-left: auto; align-items: flex-end; }
  .ag-spark span { margin-top: 2px; }
  .spark { display: block; }
  .ag-recent { list-style: none; font-size: 12px; }
  .ag-recent li { padding: 4px 0; border-bottom: 1px dashed var(--border);
                  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .ag-recent li:last-child { border-bottom: none; }
  .ag-recent .mono { color: var(--muted); margin-right: 6px; }
  .ag-foot { margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--border);
             font-size: 11px; color: var(--muted); }
  .ag-foot code { font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 10px; }
  .tl { list-style: none; font-size: 13px; }
  .tl li { padding: 8px 0 8px 2px; border-bottom: 1px solid var(--border); }
  .tl li:last-child { border-bottom: none; }
  .tl .mono { color: var(--muted); margin-right: 8px; }
  .tl-sub { font-size: 11px; color: var(--muted); margin-top: 2px; }
  .nira-card { background: linear-gradient(135deg, #1a4d3a 0%, #2d7a5a 100%);
               color: #fff; border-radius: 10px; padding: 20px 24px; margin-bottom: 24px; }
  .nira-card h2 { font-size: 18px; margin-bottom: 4px; }
  .nira-card p { font-size: 13px; opacity: 0.92; }
  @media (max-width: 768px) { .ag-grid { grid-template-columns: 1fr; } }
"""

html_out = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Agents Teatower — état &amp; évolution</title>
<style>
{CSS}
{CSS_WEEKLY}
{EXTRA}
</style>
</head>
<body>
<header>
  <h1>Agents Teatower — état &amp; évolution</h1>
  <div class="meta">Généré le {TODAY.strftime('%d/%m/%Y')}<br>
    source : journal Git du dépôt ({FIRST_LABEL} &rarr; aujourd'hui)</div>
</header>

<div class="nira-card">
  <h2>Nira — agent principal</h2>
  <p>Point d'entrée unique. Elle lit la demande, dispatche vers les
  {len(AGENTS)} spécialistes ci-dessous (en parallèle si besoin) et rend une
  seule synthèse. Prompt revu le {fr(last_edit.get('nira', '2026-05-11'))}.</p>
</div>

<div class="kpi-row">
  {kpi(len(AGENTS), "agents dans la flotte")}
  {kpi(actifs, "actifs sur 30 jours")}
  {kpi(total_missions, f"missions depuis {FIRST_LABEL}")}
  {kpi(esc(top['name']), "le plus sollicité (30j)")}
  {kpi(esc(newest_name), f"dernier né ({fr(newest[1])})")}
</div>

{section("La flotte, du plus sollicité au plus calme")}
<div class="ag-grid">{''.join(cards)}</div>

{section("Évolution")}
<div class="grid">
  {card("Volume de missions par mois", vol
        + note("Toutes missions confondues. Le décrochage de juillet-août "
               "suit les congés et la clôture, pas une perte d'usage."))}
  {card("Vie de la flotte", '<ul class="tl">' + ''.join(tl) + '</ul>')}
</div>

{section("Ce qui a changé depuis la page du 16/04/2026")}
<div class="card">
  <ul class="bullets">
    <li><b>Deux agents en plus</b> : Packaging &amp; Brand (11/05) et
        SEO Shopify (21/05) — absents de l'ancienne page.</li>
    <li><b>La file RPG est retirée.</b> Les niveaux, XP et rangs de l'ancien
        dashboard venaient de <code>data/nira_queue.json</code>, une file
        alimentée à la main et gelée au 06/07/2026. Ce qui est affiché ici est
        mesuré sur les livrables réellement commités.</li>
    <li><b>Trois agents sont devenus des skills</b> (<code>/planning-teatower</code>,
        <code>/stock-manager</code>, <code>/upload-merchandiser</code>) : invocation
        directe plutôt que dispatch par Nira.</li>
    <li><b>Livrables automatisés depuis</b> : B2B Morning Dashboard (07/08,
        publié chaque matin 7h00) et B2B Weekly Review (10/08).</li>
  </ul>
  {note("Attribution des missions : chaque commit est rattaché à un agent par "
        "mots-clés de domaine, sauf les commits « Queue: <agent> start » qui "
        "portent l'agent en clair. C'est une heuristique — un commit qui "
        "touche deux domaines est compté une seule fois, pour le premier qui "
        f"matche. {len(unmatched)} commits non attribuables sont exclus.")}
</div>

<footer>Teatower · page générée par <code>reports/build_agents_page.py</code></footer>
</body>
</html>
"""

out = ROOT / "agents" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html_out, encoding="utf-8")

print(f"OK -> {out}")
print(f"   {total_missions} missions attribuees, {len(unmatched)} non attribuees")
for r in rows:
    print(f"   {r['name']:<22} {r['total']:>4} total  {r['last30']:>3} /30j  "
          f"dernier {r['last'] or '-'}")
if unmatched:
    print("   --- non attribues (echantillon) ---")
    for d, s in unmatched[:15]:
        print(f"   {d} {s[:80]}".encode("ascii", "replace").decode("ascii"))
