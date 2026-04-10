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
    "D": (None, None),
}

# Exclusion patterns (central/corporate accounts, not physical stores)
EXCLUDE_NAMES = ["Delhaize Le Lion", "Carrefour Belgium"]

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
    partners = search_read(
        "res.partner",
        [["category_id", "in", [GMS_TAG_ID]], ["is_company", "=", True]],
        ["id", "name", "street", "city", "zip", "phone", "mobile", "email", "comment"],
    )
    # Also fetch partners that are not companies but have the tag (some stores
    # might be contacts). We'll merge and deduplicate.
    partners_contacts = search_read(
        "res.partner",
        [["category_id", "in", [GMS_TAG_ID]], ["is_company", "=", False]],
        ["id", "name", "street", "city", "zip", "phone", "mobile", "email", "comment"],
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

        if num_orders == 0:
            # Skip truly inactive (no orders AND no comment)
            if not comment:
                continue
            # Tier D — dormant / never ordered
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
                "days_overdue": 0,
                "tier": "D",
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
        })

    print(f"  Scored {len(clients)} clients.", file=sys.stderr)

    # ── 6-8. Build weekly planning ───────────────────────────────────────────
    # Sort clients: most overdue first, then by tier (A > B > C > D), then by total_ca desc
    tier_rank = {"A": 0, "B": 1, "C": 2, "D": 3}
    clients.sort(key=lambda c: (
        -c["days_overdue"],
        tier_rank.get(c["tier"], 9),
        -c["total_ca"],
    ))

    # Group by zone
    zone_clients = defaultdict(list)
    for c in clients:
        zone_clients[c["zone"]].append(c)

    # Build day assignments: 5 days (Mon-Fri), ~6 visits per day max
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

    # Flatten the ordered list by zone priority, keeping urgency order within zone
    ordered_queue = []
    for zone_name in ZONE_ORDER:
        for c in zone_clients.get(zone_name, []):
            ordered_queue.append(c)

    # Assign to days
    day_idx = 0
    for c in ordered_queue:
        if day_idx >= len(DAYS):
            break
        day_name = DAYS[day_idx]
        if len(planning[day_name]) >= MAX_VISITS_PER_DAY:
            day_idx += 1
            if day_idx >= len(DAYS):
                break
            day_name = DAYS[day_idx]

        planning[day_name].append(c)
        scheduled_ids.add(c["id"])

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
            overdue_flag = " **OVERDUE**" if v["days_overdue"] > 0 else ""
            ca_str = f"{v['ca_per_order']:.0f} EUR" if v["ca_per_order"] else "-"
            remark = truncate(v["comment"], 50)

            print(f"| {time_str} | {v['name']} | {addr} | {v['phone']} | {v['tier']} | {dsl}{overdue_flag} | {ca_str} | {remark} |")
            current_time += VISIT_DURATION + TRAVEL_BUFFER

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
    for t in ["A", "B", "C", "D"]:
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
