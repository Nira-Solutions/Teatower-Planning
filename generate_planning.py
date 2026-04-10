#!/usr/bin/env python3
"""
generate_planning.py
Connects to Odoo (XML-RPC), pulls GMS clients and order history,
calculates visit priority, and outputs an optimized weekly merchandiser
planning as Markdown.

Reusable: run each week for a fresh planning based on live Odoo data.
"""

import xmlrpc.client
from datetime import datetime, timedelta
from collections import defaultdict
import sys
import re
from urllib.parse import quote

# ── Odoo connection ──────────────────────────────────────────────────────────
URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
LOGIN = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"
GMS_TAG_ID = 27

TODAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
TODAY_STR = TODAY.strftime("%Y-%m-%d")

# ── Geographic zones (by zip prefix) ────────────────────────────────────────
def zone_for_zip(zip_code: str) -> str:
    if not zip_code:
        return "Autre"
    z = zip_code.strip()
    if not z:
        return "Autre"
    try:
        num = int(z)
    except ValueError:
        return "Autre"
    if 1000 <= num <= 1299:
        return "Bruxelles"
    if z.startswith("1"):
        return "Brabant Wallon"
    if z.startswith("4"):
        return "Liege"
    if z.startswith("5"):
        return "Namur"
    if z.startswith("6"):
        return "Luxembourg/Hainaut Sud"
    if z.startswith("7"):
        return "Hainaut"
    return "Autre"

# Zone priority for day scheduling (closest to Baillonville 5377 first)
ZONE_ORDER = [
    "Namur",
    "Liege",
    "Brabant Wallon",
    "Bruxelles",
    "Luxembourg/Hainaut Sud",
    "Hainaut",
    "Autre",
]

# ── Tier definitions ─────────────────────────────────────────────────────────
# (tier_name, min_days, max_days)
TIER_FREQ = {
    "A": (15, 20),
    "B": (25, 35),
    "C": (40, 50),
    "NEW": (7, 14),
    "D": (None, None),
}

# Exclusion patterns (central/corporate accounts, not physical stores)
EXCLUDE_NAMES = ["Delhaize Le Lion", "Carrefour Belgium"]

# Merchandiser home base
HOME_ADDRESS = "Zone d'activité Nord 33, 5377 Baillonville, Belgique"

# ── Helpers ──────────────────────────────────────────────────────────────────
def safe_str(val, default=""):
    return str(val).strip() if val else default

def strip_html(text):
    """Remove HTML tags and clean up remarks for display."""
    if not text:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    # Remove the import header line
    text = re.sub(r'---\s*Remarques merchandiser \(import Sheet\)\s*---', '', text)
    # Remove store name emoji headers
    text = re.sub(r'📍[^\n]*\n?', '', text)
    text = re.sub(r'\n+', ' | ', text.strip())
    text = re.sub(r'\s+', ' ', text).strip()
    if text.startswith('| '):
        text = text[2:]
    return text

def truncate(text, length=80):
    text = strip_html(safe_str(text))
    return (text[:length] + "...") if len(text) > length else text

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    # Connect to Odoo
    print("Connecting to Odoo...", file=sys.stderr)
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(DB, LOGIN, PASSWORD, {})
    if not uid:
        print("ERROR: Authentication failed.", file=sys.stderr)
        sys.exit(1)
    print(f"Authenticated as uid={uid}", file=sys.stderr)

    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

    def search_read(model, domain, fields, limit=0):
        return models.execute_kw(DB, uid, PASSWORD, model, "search_read",
                                 [domain], {"fields": fields, "limit": limit})

    # ── 1. Pull GMS clients (tag 27) ────────────────────────────────────────
    print("Fetching GMS clients (tag_id=27)...", file=sys.stderr)
    PARTNER_FIELDS = ["id", "name", "street", "city", "zip", "phone", "mobile",
                      "email", "comment", "create_date"]
    partners = search_read(
        "res.partner",
        [["category_id", "in", [GMS_TAG_ID]], ["is_company", "=", True]],
        PARTNER_FIELDS,
    )
    # Also fetch partners that are not companies but have the tag (some stores
    # might be contacts). We'll merge and deduplicate.
    partners_contacts = search_read(
        "res.partner",
        [["category_id", "in", [GMS_TAG_ID]], ["is_company", "=", False]],
        PARTNER_FIELDS,
    )
    seen_ids = {p["id"] for p in partners}
    for p in partners_contacts:
        if p["id"] not in seen_ids:
            partners.append(p)
            seen_ids.add(p["id"])

    print(f"  Found {len(partners)} partners with GMS tag.", file=sys.stderr)

    # ── Exclude corporate/warehouse accounts ─────────────────────────────────
    filtered = []
    for p in partners:
        name = safe_str(p.get("name"))
        if any(excl.lower() in name.lower() for excl in EXCLUDE_NAMES):
            print(f"  Excluding corporate account: {name}", file=sys.stderr)
            continue
        filtered.append(p)
    partners = filtered
    print(f"  After exclusions: {len(partners)} partners.", file=sys.stderr)

    # ── 2. Pull order history for each partner ───────────────────────────────
    print("Fetching order history...", file=sys.stderr)
    partner_ids = [p["id"] for p in partners]

    # Batch-fetch all relevant sale.orders at once
    orders = search_read(
        "sale.order",
        [
            ["partner_id", "in", partner_ids],
            ["state", "in", ["sale", "done"]],
        ],
        ["partner_id", "date_order", "amount_total"],
    )
    print(f"  Found {len(orders)} confirmed orders.", file=sys.stderr)

    # Group orders by partner
    orders_by_partner = defaultdict(list)
    for o in orders:
        pid = o["partner_id"][0] if isinstance(o["partner_id"], (list, tuple)) else o["partner_id"]
        orders_by_partner[pid].append(o)

    # ── 3-5. Calculate metrics and assign tiers ──────────────────────────────
    clients = []
    for p in partners:
        pid = p["id"]
        name = safe_str(p.get("name"))
        zip_code = safe_str(p.get("zip"))
        zone = zone_for_zip(zip_code)
        comment = safe_str(p.get("comment"))
        phone = safe_str(p.get("phone")) or safe_str(p.get("mobile"))

        ords = orders_by_partner.get(pid, [])
        num_orders = len(ords)

        # Detect new clients by create_date
        create_date_str = safe_str(p.get("create_date"))
        is_new = False
        days_since_created = 9999
        if create_date_str:
            try:
                created = datetime.strptime(create_date_str[:10], "%Y-%m-%d")
                days_since_created = (TODAY - created).days
                if days_since_created <= 60:
                    is_new = True
            except ValueError:
                pass

        if num_orders == 0:
            if is_new:
                # New client (< 60 days) with no orders yet → needs first visit
                tier = "NEW"
            elif comment:
                # Has remarks but no orders → dormant but tracked
                tier = "D"
            else:
                # No orders, no remarks, not new → skip
                continue

            clients.append({
                "id": pid,
                "name": name,
                "street": safe_str(p.get("street")),
                "city": safe_str(p.get("city")),
                "zip": zip_code,
                "zone": zone,
                "phone": phone,
                "email": safe_str(p.get("email")),
                "comment": comment,
                "num_orders": 0,
                "total_ca": 0.0,
                "ca_per_order": 0.0,
                "order_frequency": None,
                "days_since_last": None,
                "days_overdue": 50 if is_new else 0,  # NEW clients get high urgency
                "days_since_created": days_since_created,
                "tier": tier,
                "is_new": is_new,
            })
            continue

        # Parse dates and amounts
        amounts = []
        dates = []
        for o in ords:
            amounts.append(float(o.get("amount_total", 0) or 0))
            d = o.get("date_order")
            if d:
                if isinstance(d, str):
                    try:
                        dates.append(datetime.strptime(d[:10], "%Y-%m-%d"))
                    except ValueError:
                        pass
                elif isinstance(d, datetime):
                    dates.append(d)

        total_ca = sum(amounts)
        ca_per_order = total_ca / num_orders if num_orders else 0
        dates.sort()

        last_order_date = dates[-1] if dates else None
        days_since_last = (TODAY - last_order_date).days if last_order_date else 9999

        # Order frequency: average days between consecutive orders
        if len(dates) >= 2:
            intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
            order_frequency = sum(intervals) / len(intervals)
        else:
            order_frequency = None

        # Dormant check: last order > 180 days ago
        if days_since_last > 180:
            tier = "D"
        elif ca_per_order >= 500 and total_ca >= 4000:
            tier = "A"
        elif ca_per_order >= 300 and total_ca >= 2000:
            tier = "B"
        else:
            tier = "C"

        # Calculate overdue days based on tier max frequency
        if tier in ("A", "B", "C"):
            _, max_freq = TIER_FREQ[tier]
            days_overdue = max(0, days_since_last - max_freq)
        else:
            days_overdue = 0

        # New clients with few orders (< 3) get a boost: treat as Tier B minimum
        # to ensure follow-up visits while the relationship is being established
        if is_new and num_orders <= 3 and tier in ("C", "D"):
            tier = "B"

        clients.append({
            "id": pid,
            "name": name,
            "street": safe_str(p.get("street")),
            "city": safe_str(p.get("city")),
            "zip": zip_code,
            "zone": zone,
            "phone": phone,
            "email": safe_str(p.get("email")),
            "comment": comment,
            "num_orders": num_orders,
            "total_ca": total_ca,
            "ca_per_order": ca_per_order,
            "order_frequency": order_frequency,
            "days_since_last": days_since_last,
            "days_overdue": days_overdue,
            "tier": tier,
            "is_new": is_new,
            "days_since_created": days_since_created,
        })

    # Count new clients
    new_count = sum(1 for c in clients if c.get("is_new"))
    print(f"  Scored {len(clients)} clients ({new_count} nouveaux < 60j).", file=sys.stderr)

    # ── 6-8. Build weekly planning ───────────────────────────────────────────
    tier_rank = {"A": 0, "B": 1, "C": 2, "D": 3}

    # Group by zone
    zone_clients = defaultdict(list)
    for c in clients:
        zone_clients[c["zone"]].append(c)

    # Sort each zone: overdue first, then tier, then CA
    for zone_name in zone_clients:
        zone_clients[zone_name].sort(key=lambda c: (
            -c["days_overdue"],
            tier_rank.get(c["tier"], 9),
            -c["total_ca"],
        ))

    DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    # Next Monday from today
    days_until_monday = (7 - TODAY.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    week_monday = TODAY + timedelta(days=days_until_monday)
    VISIT_DURATION = timedelta(minutes=30)
    TRAVEL_BUFFER = timedelta(minutes=15)
    MAX_VISITS_PER_DAY = 6

    planning = {d: [] for d in DAYS}
    scheduled_ids = set()

    # ── Zone-day mapping ────────────────────────────────────────────────────
    # Reserve specific days for geographic zones to guarantee coverage.
    # Proximity to Baillonville (5377): Namur closest, then Liège, then BW, etc.
    ZONE_DAY_MAP = {
        "Lundi":    ["Namur"],
        "Mardi":    ["Namur", "Luxembourg/Hainaut Sud"],
        "Mercredi": ["Liege"],
        "Jeudi":    ["Brabant Wallon", "Liege"],
        "Vendredi": ["Bruxelles", "Hainaut", "Autre"],
    }

    # ── Priority scoring for selection ──────────────────────────────────────
    def visit_priority(c):
        """Higher = more urgent to visit this week."""
        score = 0
        # NEW clients get high priority (first visit / relationship building)
        if c.get("is_new"):
            score += 80
        # Overdue clients get massive priority
        score += c["days_overdue"] * 10
        # Tier A/B approaching deadline (>70% of max freq) should be included
        if c["tier"] in ("A", "B", "C"):
            _, max_freq = TIER_FREQ[c["tier"]]
            if c["days_since_last"] is not None:
                pct = c["days_since_last"] / max_freq
                if pct > 0.7:
                    score += pct * 50
        # Tier bonus (A > B > C > D)
        tier_bonus = {"A": 40, "B": 20, "C": 5, "D": 0, "NEW": 60}
        score += tier_bonus.get(c["tier"], 0)
        # CA bonus
        score += min(c["total_ca"] / 200, 30)
        return score

    # ── Fill each day ───────────────────────────────────────────────────────
    for day_name in DAYS:
        zones_for_day = ZONE_DAY_MAP[day_name]
        candidates = []
        for z in zones_for_day:
            for c in zone_clients.get(z, []):
                if c["id"] not in scheduled_ids and c["tier"] not in ("D",):
                    candidates.append(c)

        # Sort by priority (highest first)
        candidates.sort(key=lambda c: -visit_priority(c))

        # Pick top N
        for c in candidates[:MAX_VISITS_PER_DAY]:
            planning[day_name].append(c)
            scheduled_ids.add(c["id"])

    # ── Fill remaining slots with best overdue from any zone ────────────────
    all_remaining = [c for c in clients if c["id"] not in scheduled_ids and c["tier"] != "D"]
    all_remaining.sort(key=lambda c: -visit_priority(c))

    for day_name in DAYS:
        while len(planning[day_name]) < MAX_VISITS_PER_DAY and all_remaining:
            # Find best remaining client compatible with this day's zones
            added = False
            for i, c in enumerate(all_remaining):
                if c["id"] not in scheduled_ids:
                    planning[day_name].append(c)
                    scheduled_ids.add(c["id"])
                    all_remaining.pop(i)
                    added = True
                    break
            if not added:
                break

    # ── 9. Output as Markdown ────────────────────────────────────────────────
    week_start = week_monday
    week_end = week_monday + timedelta(days=4)
    print(f"\n# Planning Merchandiser — Semaine du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}\n")
    print(f"**Base**: Baillonville (5377) | **Horaire**: 08h30 - 16h30 | **Duree visite**: 30 min + 15 min trajet\n")
    print(f"**Genere le**: {TODAY_STR} | **Clients GMS scores**: {len(clients)}\n")

    for day_i, day_name in enumerate(DAYS):
        visits = planning[day_name]
        if not visits:
            continue

        # Sort visits within the day: Hyper first (morning constraint)
        def is_hyper(c):
            n = c["name"].lower()
            return "hyper" in n or "hypermar" in n
        visits.sort(key=lambda c: (0 if is_hyper(c) else 1))
        planning[day_name] = visits

        day_date = week_start + timedelta(days=day_i)
        print(f"\n## {day_name} {day_date.strftime('%d/%m/%Y')}\n")

        # Determine main zone(s) for the day
        day_zones = list(dict.fromkeys(v["zone"] for v in visits))
        print(f"**Zone(s)**: {', '.join(day_zones)}\n")

        print("| Heure | Magasin | Adresse | Tel | Tier | Derniere cde | CA moy/cde | Remarques |")
        print("|-------|---------|---------|-----|------|-------------|------------|-----------|")

        current_time = datetime(day_date.year, day_date.month, day_date.day, 8, 30)
        for v in visits:
            time_str = current_time.strftime("%Hh%M")
            addr = f"{safe_str(v['street'])}, {safe_str(v['zip'])} {safe_str(v['city'])}"
            dsl = f"{v['days_since_last']}j" if v['days_since_last'] is not None else "jamais"
            if v.get("is_new") and v["num_orders"] == 0:
                overdue_flag = " **NOUVEAU**"
            elif v.get("is_new"):
                overdue_flag = " **NOUVEAU**" + (" **OVERDUE**" if v["days_overdue"] > 0 else "")
            elif v["days_overdue"] > 0:
                overdue_flag = " **OVERDUE**"
            else:
                overdue_flag = ""
            ca_str = f"{v['ca_per_order']:.0f} EUR" if v["ca_per_order"] else "-"
            remark = truncate(v["comment"], 50)

            print(f"| {time_str} | {v['name']} | {addr} | {v['phone']} | {v['tier']} | {dsl}{overdue_flag} | {ca_str} | {remark} |")
            current_time += VISIT_DURATION + TRAVEL_BUFFER

        # Generate Google Maps route link (home → visits → home)
        waypoints = [HOME_ADDRESS]
        for v in visits:
            addr_full = f"{safe_str(v['street'])}, {safe_str(v['zip'])} {safe_str(v['city'])}, Belgique"
            waypoints.append(addr_full)
        waypoints.append(HOME_ADDRESS)
        gmaps_path = "/".join(quote(w, safe="") for w in waypoints)
        gmaps_url = f"https://www.google.com/maps/dir/{gmaps_path}"

        print(f"\n**[Ouvrir l'itineraire dans Google Maps]({gmaps_url})**")

    # ── 10. Summary table ────────────────────────────────────────────────────
    print("\n---\n")
    print("## Resume\n")

    tier_counts = defaultdict(int)
    tier_scheduled = defaultdict(int)
    for c in clients:
        tier_counts[c["tier"]] += 1
    for day_name in DAYS:
        for v in planning[day_name]:
            tier_scheduled[v["tier"]] += 1

    print("| Tier | Total clients | Planifies cette semaine | Frequence cible |")
    print("|------|--------------|------------------------|-----------------|")
    for t in ["A", "B", "C", "NEW", "D"]:
        freq = TIER_FREQ[t]
        freq_str = f"{freq[0]}-{freq[1]}j" if freq[0] else "sur demande"
        print(f"| {t} | {tier_counts[t]} | {tier_scheduled[t]} | {freq_str} |")

    total_scheduled = sum(len(v) for v in planning.values())
    print(f"\n**Total visites planifiees**: {total_scheduled} / {len(clients)} clients actifs\n")

    # Overdue summary
    overdue_clients = [c for c in clients if c["days_overdue"] > 0]
    if overdue_clients:
        print(f"### Clients en retard de visite ({len(overdue_clients)})\n")
        print("| Magasin | Zone | Tier | Jours retard | Derniere cde | Planifie ? |")
        print("|---------|------|------|-------------|-------------|------------|")
        for c in sorted(overdue_clients, key=lambda x: -x["days_overdue"]):
            status = "Oui" if c["id"] in scheduled_ids else "Non"
            print(f"| {c['name']} | {c['zone']} | {c['tier']} | +{c['days_overdue']}j | {c['days_since_last']}j | {status} |")

    # Clients NOT scheduled
    not_scheduled = [c for c in clients if c["id"] not in scheduled_ids]
    if not_scheduled:
        print(f"\n### Clients NON planifies cette semaine ({len(not_scheduled)})\n")
        print("| Magasin | Zone | Tier | CA total | Derniere cde | Raison |")
        print("|---------|------|------|---------|-------------|--------|")
        for c in sorted(not_scheduled, key=lambda x: (-x["total_ca"])):
            dsl = f"{c['days_since_last']}j" if c['days_since_last'] is not None else "jamais"
            if c["tier"] == "D":
                reason = "Dormant"
            elif c["days_overdue"] == 0:
                reason = "Pas encore en retard"
            else:
                reason = "Capacite semaine atteinte"
            print(f"| {c['name']} | {c['zone']} | {c['tier']} | {c['total_ca']:.0f} EUR | {dsl} | {reason} |")

    print("\n---\n*Planning genere automatiquement depuis Odoo. Relancer `python generate_planning.py` chaque semaine.*\n")


if __name__ == "__main__":
    main()
