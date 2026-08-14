"""
build_planning_pool.py — Source unique Odoo pour la planification merchandiser.

Dérive en temps réel la liste maître des magasins GMS à visiter, sans dépendre
du fichier `Displays Teatower B2B.xlsx`. Remplace la méthode §0 v1 (scan Excel)
par §0 v2 (scan Odoo).

Logique :
  - identifie tous les partners "magasins GMS" via leur parent_id (Delhaize Le Lion,
    Carrefour Belgium, ...) + les indépendants (Spar, Intermarché, AD) via name pattern
  - calcule pour chacun : Statut, avg_mois, Tier, cycle, last_visit_effective, next_visit
  - sortie : liste markdown + CSV (data/planning_pool_YYYY-MM-DD.{md,csv})

Convention pour last_visit_effective :
  max(
    max(stock.picking outgoing done où partner_shipping_id = magasin),
    max([VISITE YYYY-MM-DD] parsés dans res.partner.comment)
  )

Convention pour last_so_date (CHAMP DÉDIÉ — règle Nicolas 21/05/2026) :
  max(date_order) sur sale.order où state ∈ ['sale','done']
  et (partner_id = pid OR partner_shipping_id = pid OR partner_invoice_id = pid)
  → C'EST LA SEULE SOURCE DE VÉRITÉ pour "dernière visite client".
  → NE JAMAIS se baser sur les anciens fichiers planning .md/.html du repo
    (un magasin inscrit dans un planning passé n'a pas forcément été visité).
  → Champs exposés : last_so_date (ISO), last_so_days_ago (int), last_so_label
    (format "JJ/MM/AAAA (Xj)" ou "Jamais commandé").

Convention pour Statut :
  - res.partner.sale_warn == 'block' AND comment contient '[ARRET' → Arret
  - sinon → Actif

Convention pour Tier :
  - avg_mois ≥ 400€        → A (cycle 21j)
  - avg_mois 100-400€      → B (cycle 28j)
  - avg_mois 30-100€       → C (cycle 42j)
  - avg_mois < 30€         → X (cycle 90j)

Usage : python build_planning_pool.py [--target-date YYYY-MM-DD]
"""

import xmlrpc.client
import argparse
import csv
import re
from datetime import datetime, date, timedelta
from collections import defaultdict
from pathlib import Path

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"

# Patterns identifiant un magasin GMS
GMS_PARENT_NAMES = [
    "Delhaize Le Lion",
    "Carrefour Belgium",
]
GMS_NAME_TOKENS = [
    "Intermarch",
    "Spar ",
    "Spar-",
    " AD ",
    "AD Delhaize",
    "Proxy Delhaize",
    "Affili",  # Affilié XXX - Delhaize/AD/...
    "Carrefour Market",
    "Carrefour Hyper",
    "Hyper Carrefour",
    "Carrefour Express",
    "CARREFOUR MARKET",
    "Delhaize ",
]

TIER_RULES = [
    (400.0, "A", 21),
    (100.0, "B", 28),
    (30.0, "C", 42),
    (0.0, "X", 90),
]

VISITE_TAG_RE = re.compile(r"\[VISITE (\d{4}-\d{2}-\d{2})", re.IGNORECASE)

# Tags merchandiser terrain (Nicolas 10/06/2026) — parsés depuis res.partner.comment
# et exposés dans le planning sous chaque magasin (remplacent les "notes" verbeuses).
#   [STOCK: réserve]            -> CONTROLE STOCK : où contrôler le stock avant remplissage
#   [REASSORT: GUN]             -> METHODE REASSORT : méthode de remplissage (gun, manuel, ...)
#   [REGLE: étiquettes+antivol] -> REGLE MAGASIN : règle spécifique magasin
STOCK_RE = re.compile(r"\[STOCK:\s*([^\]]+)\]", re.IGNORECASE)
REASSORT_RE = re.compile(r"\[REASSORT:\s*([^\]]+)\]", re.IGNORECASE)
REGLE_RE = re.compile(r"\[REGLE:\s*([^\]]+)\]", re.IGNORECASE)

# Overrides de cadence (jours) par magasin — priment sur le cycle déduit du Tier.
# Clé = pid Odoo. Voir REGLES.md §5.
CADENCE_OVERRIDE_PID = {
    2927: 28,    # Distriparenthese - Intermarché Gosselies (Nicolas 20/04/2026)
    122944: 25,  # Lambertdis SRL - Spar Manhay : espacer les réassorts (Nicolas 10/06/2026)
    7760: 30,    # Hyper Carrefour Fleron : pas de passage avant 30j (Nicolas 24/06/2026)
    113498: 30,  # Affilié 044471 - Delhaize Materne : pas de passage avant 30j (Nicolas 24/06/2026)
    8779: 30,    # Affilié 044780 - Proxy Delhaize Le Beau Rivage : cadence 30j (Nicolas 24/06/2026)
    123144: 15,  # Affilié 040490 - Delhaize Ath : merch permanent, cadence 15j (Nicolas 28/06/2026)
    123297: 30,  # Spar Gembloux (fiche livraison Pascal Gilson) : passage mensuel demandé par le magasin (Nicolas 14/08/2026)
}


def parse_tag_field(comment, regex):
    """Extrait la valeur d'un tag [CLE: valeur] du comment (HTML strippé), sinon ''."""
    if not comment:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(comment))
    m = regex.search(text)
    return m.group(1).strip() if m else ""

# Règle dure : nom magasin TOUJOURS affiché en clair (jamais l'ID seul, jamais un prefix numérique).
# Si le store_name est vide ou commence par un ID Odoo numérique (≥4 chiffres), fallback billing_partner
# puis fallback "Enseigne — ville" déduit du billing_partner / parent_name.
NUMERIC_PREFIX_RE = re.compile(r"^\s*\d{4,}\s*[-_:.\s]*")


def clean_store_name(raw):
    """Strip un éventuel prefix numérique (ID Odoo) du nom magasin."""
    if not raw:
        return ""
    s = str(raw).strip()
    s = NUMERIC_PREFIX_RE.sub("", s).strip()
    return s


def display_name(store_name, billing_partner, parent_name, city, pid):
    """
    Retourne TOUJOURS un libellé lisible du magasin — JAMAIS l'ID seul.
    Priorité :
      1. store_name nettoyé (sans prefix numérique)
      2. billing_partner nettoyé (souvent "Société - Enseigne Ville")
      3. parent_name + ville (ex "Carrefour Belgium — Liège") avec mention "sans nom propre"
      4. ultime fallback : "Magasin #pid — ville"
    """
    n1 = clean_store_name(store_name)
    if n1:
        return n1
    n2 = clean_store_name(billing_partner)
    if n2:
        return n2
    if parent_name:
        return f"{parent_name} {city or ''} — sans nom propre".strip(" —")
    return f"Magasin #{pid} {city or ''} — sans nom propre".strip(" —")


def connect():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    return uid, models


def is_gms_partner(partner, parent_name):
    name = (partner.get("name") or "")
    if parent_name:
        for chain in GMS_PARENT_NAMES:
            if chain in parent_name:
                return True
    for token in GMS_NAME_TOKENS:
        if token in name:
            return True
    return False


def compute_tier(avg_mois, first_so_date=None, today=None, so_count=0):
    """
    Override Tier nouveau client : si first_so >= today - 90j ET au moins 1 SO,
    le client a été implanté récemment → minimum Tier B (cycle 28j) car on lui
    accorde un suivi merchandiser standard pendant la phase de démarrage,
    indépendamment de l'avg_mois encore faible (1 SO / 12 mois = avg artificiellement bas).
    """
    base_tier, base_cycle = "X", 90
    for threshold, tier, cycle in TIER_RULES:
        if avg_mois >= threshold:
            base_tier, base_cycle = tier, cycle
            break

    if first_so_date and today and so_count >= 1:
        days_since_first = (today - first_so_date).days
        if days_since_first <= 90:
            # override : on force au minimum B (Tier C si avg_mois suffit pour C, mais
            # B en démarrage pour un suivi rapproché)
            if base_tier in ("X", "C"):
                return "B", 28
    return base_tier, base_cycle


def parse_visit_dates_from_comment(comment):
    if not comment:
        return []
    if not isinstance(comment, str):
        return []
    # strip HTML tags
    text = re.sub(r"<[^>]+>", " ", comment)
    dates = []
    for m in VISITE_TAG_RE.finditer(text):
        try:
            dates.append(date.fromisoformat(m.group(1)))
        except ValueError:
            pass
    return dates


def has_arret_tag(comment, sale_warn):
    if sale_warn != "block":
        return False
    if not comment:
        return False
    text = str(comment)
    return "[ARRET" in text


def has_no_merch_tag(comment):
    """Magasin qui passe commande seul — pas de suivi merchandiser (tag [NO-MERCH).

    Le gérant/la gérante commande de lui-même : on ne l'inscrit jamais au planning
    Gilles (visites/implantations). Indépendant du sale_warn (le magasin reste un
    client actif, on lui livre toujours, on ne le visite simplement plus).
    Ex. : AD Soumagne Marvan #2915, Carrefour Market Naninne #9079 (Nicolas 29/05/2026).
    """
    if not comment:
        return False
    return "[NO-MERCH" in str(comment)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-date", default=date.today().isoformat(),
                        help="Date de référence (today par défaut). Format YYYY-MM-DD.")
    parser.add_argument("--lookback-months", type=int, default=12,
                        help="Fenêtre de calcul avg_mois (mois). Défaut 12.")
    parser.add_argument("--out-dir", default=r"C:\Users\FlowUP\OneDrive\Teatower\data",
                        help="Répertoire de sortie.")
    args = parser.parse_args()

    today = date.fromisoformat(args.target_date)
    lookback = today - timedelta(days=30 * args.lookback_months)

    # EXCLUSIVITE (Nicolas 09/06/2026) : les magasins du pool TELEVENTE (Vanessa)
    # sortent du cycle de VISITES merch de Gilles. Pools exclusifs. On lit la
    # derniere liste televente_pool_*.csv (produite par build_televente_pool.py,
    # a lancer AVANT) -> ces pids passent en statut "Televente".
    # NB : les implantations (nouveau client sans SO) ne sont pas dans ce pool,
    # donc elles restent merch -> aucun conflit pour l'implantation.
    televente_pids = set()
    tv_csvs = sorted(Path(args.out_dir).glob("televente_pool_*.csv"))
    if tv_csvs:
        with tv_csvs[-1].open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    televente_pids.add(int(row["pid"]))
                except (KeyError, ValueError):
                    pass
        print(f"[*] Exclusivite : {len(televente_pids)} magasins televente lus depuis {tv_csvs[-1].name}")
    else:
        print("[!] Aucun televente_pool_*.csv -> exclusivite non appliquee (lance build_televente_pool.py avant)")

    uid, models = connect()
    print(f"[*] Odoo connecté uid={uid} | target_date={today} | lookback={lookback}\n")

    # 1bis) Tous les partners explicitement marqués Arret (sale_warn=block + [ARRET dans comment)
    # même sans SO récente — pour ne perdre aucun Arret du pool
    print("[*] Pull partners explicitement Arret (sale_warn=block + [ARRET tag)...")
    arret_partners = models.execute_kw(
        DB, uid, PASSWORD,
        "res.partner", "search_read",
        [[("sale_warn", "=", "block"),
          ("comment", "ilike", "[ARRET")]],
        {"fields": ["id", "name", "parent_id", "street", "city", "zip",
                    "phone", "mobile", "email", "comment",
                    "sale_warn", "sale_warn_msg", "category_id",
                    "active", "is_company"]}
    )
    print(f"    {len(arret_partners)} partners Arret marqués")

    # 1) Tous les SO confirmés depuis lookback (pour calcul avg_mois)
    print("[*] Pull sale.order confirmés...")
    sos = models.execute_kw(
        DB, uid, PASSWORD,
        "sale.order", "search_read",
        [[("state", "in", ["sale", "done"]),
          ("date_order", ">=", lookback.isoformat())]],
        {"fields": ["id", "name", "partner_id", "partner_shipping_id",
                    "date_order", "amount_untaxed", "amount_total"]}
    )
    print(f"    {len(sos)} SO confirmées sur la fenêtre {args.lookback_months} mois")

    # 2) Tous les pickings outgoing done (pour last_visit "réassort")
    print("[*] Pull stock.picking outgoing done...")
    pickings = models.execute_kw(
        DB, uid, PASSWORD,
        "stock.picking", "search_read",
        [[("state", "=", "done"),
          ("picking_type_code", "=", "outgoing"),
          ("date_done", ">=", (today - timedelta(days=400)).isoformat())]],
        {"fields": ["id", "name", "partner_id", "date_done"]}
    )
    print(f"    {len(pickings)} pickings outgoing done sur 400 jours")

    # 3) Tous les partners référencés
    pids = set()
    for s in sos:
        if s["partner_id"]: pids.add(s["partner_id"][0])
        if s["partner_shipping_id"]: pids.add(s["partner_shipping_id"][0])
    for p in pickings:
        if p["partner_id"]: pids.add(p["partner_id"][0])
    # Inclure aussi les Arret connus
    for ap in arret_partners:
        pids.add(ap["id"])

    print(f"[*] Read {len(pids)} partners...")
    partners = models.execute_kw(
        DB, uid, PASSWORD,
        "res.partner", "read",
        [list(pids)],
        {"fields": ["id", "name", "parent_id", "street", "city", "zip",
                    "phone", "mobile", "email", "comment",
                    "sale_warn", "sale_warn_msg", "category_id",
                    "active", "is_company"]}
    )
    pmap = {p["id"]: p for p in partners}

    # 4) Agrégation par "magasin réel"
    # On utilise comme clé le partner_shipping_id (sinon partner_id).
    # Le but : le magasin physique. La facturation peut être ailleurs (Carrefour Belgium central),
    # mais c'est le SHIP qui correspond au point de vente.
    store_agg = defaultdict(lambda: {
        "store_pid": None,
        "store_name": "",
        "billing_partner": "",
        "city": "", "zip": "", "street": "",
        "phone": "", "email": "",
        "comment": "",
        "sale_warn": "no-message",
        "parent_name": "",
        "so_count": 0,
        "total_untaxed_12m": 0.0,
        "last_so_date": None,
        "first_so_date": None,
        "categories": [],
    })

    for s in sos:
        ship_pid = s["partner_shipping_id"][0] if s["partner_shipping_id"] else None
        billing_pid = s["partner_id"][0] if s["partner_id"] else None
        store_pid = ship_pid or billing_pid
        if not store_pid:
            continue
        p = pmap.get(store_pid)
        if not p:
            continue
        parent_name = p.get("parent_id")[1] if p.get("parent_id") else ""
        if not is_gms_partner(p, parent_name):
            # Test aussi le partner facturation au cas où le ship n'a pas de pattern
            bp = pmap.get(billing_pid, {})
            bp_parent = bp.get("parent_id")[1] if bp.get("parent_id") else ""
            if not is_gms_partner(bp, bp_parent):
                continue

        rec = store_agg[store_pid]
        if rec["store_pid"] is None:
            rec["store_pid"] = store_pid
            rec["store_name"] = p.get("name", "") or ""
            rec["billing_partner"] = pmap.get(billing_pid, {}).get("name", "") or ""
            rec["city"] = p.get("city") or ""
            rec["zip"] = p.get("zip") or ""
            rec["street"] = p.get("street") or ""
            rec["phone"] = p.get("phone") or p.get("mobile") or ""
            rec["email"] = p.get("email") or ""
            rec["comment"] = p.get("comment") or ""
            rec["sale_warn"] = p.get("sale_warn") or "no-message"
            rec["parent_name"] = parent_name
            rec["categories"] = p.get("category_id") or []
        rec["so_count"] += 1
        rec["total_untaxed_12m"] += s.get("amount_untaxed") or 0.0
        d = date.fromisoformat(s["date_order"][:10])
        if rec["last_so_date"] is None or d > rec["last_so_date"]:
            rec["last_so_date"] = d
        if rec["first_so_date"] is None or d < rec["first_so_date"]:
            rec["first_so_date"] = d

    # 4bis) Inclure aussi les Arret connus qui n'auraient pas été agrégés par les SO
    # (typiquement Arret sans SO 12m → cohérent puisqu'ils ne livrent plus)
    for ap in arret_partners:
        pid = ap["id"]
        parent_name = ap["parent_id"][1] if ap.get("parent_id") else ""
        # On inclut ces partners s'ils ressemblent à du GMS OU si on a une raison de penser
        # qu'ils sont GMS (sale_warn block + tag ARRET = forte présomption Teatower B2B)
        if pid in store_agg:
            continue
        is_gms = is_gms_partner(ap, parent_name)
        if not is_gms:
            # Si le tag ARRET est présent, considère que c'est un client B2B suivi (sinon
            # il n'aurait pas été marqué) — on l'inclut quand même
            pass  # inclus quand même
        rec = store_agg[pid]
        rec["store_pid"] = pid
        rec["store_name"] = ap.get("name", "") or ""
        rec["billing_partner"] = parent_name  # à défaut
        rec["city"] = ap.get("city") or ""
        rec["zip"] = ap.get("zip") or ""
        rec["street"] = ap.get("street") or ""
        rec["phone"] = ap.get("phone") or ap.get("mobile") or ""
        rec["email"] = ap.get("email") or ""
        rec["comment"] = ap.get("comment") or ""
        rec["sale_warn"] = ap.get("sale_warn") or "no-message"
        rec["parent_name"] = parent_name
        rec["categories"] = ap.get("category_id") or []
        # so_count/total_untaxed/last_so_date restent à 0/None — c'est juste qu'ils
        # n'ont pas de SO sur la fenêtre, mais ils existent

    # 5) Dernière "visite réassort" = dernier picking done par store_pid
    last_picking = {}
    for pk in pickings:
        ppid = pk["partner_id"][0] if pk["partner_id"] else None
        if ppid in store_agg:
            d = date.fromisoformat(pk["date_done"][:10]) if pk["date_done"] else None
            if d:
                if ppid not in last_picking or d > last_picking[ppid]:
                    last_picking[ppid] = d

    # 6) Construction de la liste finale
    rows = []
    for pid, r in store_agg.items():
        avg_mois = r["total_untaxed_12m"] / max(args.lookback_months, 1)
        tier, cycle = compute_tier(
            avg_mois,
            first_so_date=r["first_so_date"],
            today=today,
            so_count=r["so_count"],
        )
        # Override cadence par magasin (REGLES.md §5) — prime sur le cycle du Tier.
        cycle_override = CADENCE_OVERRIDE_PID.get(pid)
        if cycle_override:
            cycle = cycle_override

        if has_arret_tag(r["comment"], r["sale_warn"]):
            statut = "Arret"
        elif has_no_merch_tag(r["comment"]):
            statut = "NoMerch"  # commande en autonomie — exclu des visites/implantations
        elif pid in televente_pids:
            statut = "Televente"  # suivi par Vanessa (appels) — exclu des visites Gilles
        else:
            statut = "Actif"

        # last_visit_effective = max(last_picking, max([VISITE …] dans comment), last_so)
        candidates = []
        if pid in last_picking:
            candidates.append(("picking", last_picking[pid]))
        for d in parse_visit_dates_from_comment(r["comment"]):
            candidates.append(("comment_tag", d))
        if r["last_so_date"]:
            candidates.append(("last_so", r["last_so_date"]))
        last_visit, last_source = (None, None)
        if candidates:
            last_source, last_visit = max(candidates, key=lambda x: x[1])
        next_visit = last_visit + timedelta(days=cycle) if last_visit else None
        retard_j = (today - next_visit).days if next_visit and next_visit < today else 0

        display = display_name(
            r["store_name"], r["billing_partner"], r["parent_name"], r["city"], pid
        )

        # Champs terrain merchandiser (tags Odoo) — affichés sous le magasin
        controle_stock = parse_tag_field(r["comment"], STOCK_RE)
        methode_reassort = parse_tag_field(r["comment"], REASSORT_RE)
        regle_magasin = parse_tag_field(r["comment"], REGLE_RE)

        # last_so_date enrichi : ancienneté + label lisible (règle Nicolas 21/05/2026)
        # "Dernière visite client" dans le planning = dernière SO confirmée.
        # JAMAIS extrapolé depuis les anciens .md/.html du repo planning.
        if r["last_so_date"]:
            last_so_days_ago = (today - r["last_so_date"]).days
            last_so_label = f"{r['last_so_date'].strftime('%d/%m/%Y')} ({last_so_days_ago}j)"
        else:
            last_so_days_ago = None
            last_so_label = "Jamais commandé"

        rows.append({
            "pid": pid,
            "store_name": r["store_name"],
            "display_name": display,
            "parent_name": r["parent_name"],
            "billing_partner": r["billing_partner"],
            "street": r["street"], "zip": r["zip"], "city": r["city"],
            "phone": r["phone"], "email": r["email"],
            "statut": statut,
            "sale_warn": r["sale_warn"],
            "tier": tier, "cycle_days": cycle,
            "so_count_12m": r["so_count"],
            "total_untaxed_12m": round(r["total_untaxed_12m"], 2),
            "avg_mois": round(avg_mois, 2),
            "first_so_date": r["first_so_date"].isoformat() if r["first_so_date"] else "",
            "last_so_date": r["last_so_date"].isoformat() if r["last_so_date"] else "",
            "last_so_days_ago": last_so_days_ago if last_so_days_ago is not None else "",
            "last_so_label": last_so_label,
            "last_visit": last_visit.isoformat() if last_visit else "",
            "last_visit_source": last_source or "",
            "next_visit": next_visit.isoformat() if next_visit else "",
            "retard_j": retard_j,
            "controle_stock": controle_stock,
            "methode_reassort": methode_reassort,
            "regle_magasin": regle_magasin,
        })

    # 7) Tri : Actif d'abord, retard décroissant, Tier A>B>C>X, CA total décroissant
    tier_order = {"A": 0, "B": 1, "C": 2, "X": 3}
    rows.sort(key=lambda r: (
        0 if r["statut"] == "Actif" else 1,
        -r["retard_j"],
        tier_order.get(r["tier"], 9),
        -r["total_untaxed_12m"],
    ))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = today.isoformat()

    # CSV
    csv_path = out_dir / f"planning_pool_{stamp}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n[+] CSV : {csv_path}")

    # Markdown synthèse
    md_path = out_dir / f"planning_pool_{stamp}.md"
    actifs = [r for r in rows if r["statut"] == "Actif"]
    arret = [r for r in rows if r["statut"] == "Arret"]
    no_merch = [r for r in rows if r["statut"] == "NoMerch"]
    televente = [r for r in rows if r["statut"] == "Televente"]
    overdue = [r for r in actifs if r["retard_j"] > 0]
    tier_counts = defaultdict(int)
    for r in actifs:
        tier_counts[r["tier"]] += 1

    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# Planning pool — GMS (source Odoo, généré {stamp})\n\n")
        f.write(f"- **Magasins GMS uniques** : {len(rows)}\n")
        f.write(f"  - Actifs : {len(actifs)} (Tier A={tier_counts['A']}, B={tier_counts['B']}, C={tier_counts['C']}, X={tier_counts['X']})\n")
        f.write(f"  - Arret  : {len(arret)}\n")
        f.write(f"  - NoMerch (commande seul, hors planning) : {len(no_merch)}\n")
        f.write(f"  - Televente (suivi Vanessa, hors visites Gilles) : {len(televente)}\n")
        f.write(f"- **OVERDUE Actifs** (next_visit < {stamp}) : {len(overdue)}\n\n")
        f.write(f"## OVERDUE — par retard décroissant\n\n")
        f.write("| Tier | Retard | Magasin | Adresse | Cycle | Dernière SO | Last visit | Source | Next visit | avg/mois |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        for r in overdue[:200]:
            adresse = f"{r['street']}, {r['zip']} {r['city']}".strip(", ")
            # Règle dure : nom magasin TOUJOURS en clair (display_name) — pid en suffixe seulement
            label = f"{r['display_name']} (#{r['pid']})"
            f.write(f"| {r['tier']} | **{r['retard_j']}j** | {label} | {adresse} | {r['cycle_days']}j | {r['last_so_label']} | {r['last_visit']} | {r['last_visit_source']} | {r['next_visit']} | {r['avg_mois']:.0f}€ |\n")
        f.write("\n")
        f.write(f"## Tous Actifs (premiers 50 par retard puis Tier)\n\n")
        f.write("| Statut | Tier | Magasin | Dernière SO | Last visit | Next visit | Retard | avg/mois | SO 12m |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for r in actifs[:50]:
            label = f"{r['display_name']} (#{r['pid']})"
            f.write(f"| {r['statut']} | {r['tier']} | {label} | {r['last_so_label']} | {r['last_visit']} | {r['next_visit']} | {r['retard_j']}j | {r['avg_mois']:.0f}€ | {r['so_count_12m']} |\n")
        if no_merch:
            f.write(f"\n## NoMerch — EXCLUS du planning (commande en autonomie)\n\n")
            f.write("> Le gérant/la gérante passe commande seul(e). Ne JAMAIS inscrire au planning Gilles (tag `[NO-MERCH` dans res.partner.comment Odoo).\n\n")
            f.write("| Magasin | Adresse | Dernière SO | avg/mois |\n")
            f.write("|---|---|---|---|\n")
            for r in no_merch:
                adresse = f"{r['street']}, {r['zip']} {r['city']}".strip(", ")
                f.write(f"| {r['display_name']} (#{r['pid']}) | {adresse} | {r['last_so_label']} | {r['avg_mois']:.0f}€ |\n")
        if televente:
            f.write(f"\n## Televente — EXCLUS des visites Gilles (suivi Vanessa par appels)\n\n")
            f.write("> Pool exclusif télévente (réfs≤10 OU dist>60km & réfs<20). Réassort par téléphone (Vanessa). "
                    "L'implantation initiale reste merch. Voir planning télévente.\n\n")
            f.write("| Magasin | Adresse | Dernière SO | avg/mois |\n")
            f.write("|---|---|---|---|\n")
            for r in televente:
                adresse = f"{r['street']}, {r['zip']} {r['city']}".strip(", ")
                f.write(f"| {r['display_name']} (#{r['pid']}) | {adresse} | {r['last_so_label']} | {r['avg_mois']:.0f}€ |\n")
    print(f"[+] Markdown : {md_path}")

    print(f"\n[*] Synthèse :")
    print(f"    Magasins GMS uniques : {len(rows)}")
    print(f"    Actifs : {len(actifs)} | Arret : {len(arret)} | NoMerch : {len(no_merch)} | Televente : {len(televente)}")
    print(f"    Distribution Tier (Actifs) : A={tier_counts['A']} B={tier_counts['B']} C={tier_counts['C']} X={tier_counts['X']}")
    print(f"    OVERDUE actifs : {len(overdue)}")


if __name__ == "__main__":
    main()
