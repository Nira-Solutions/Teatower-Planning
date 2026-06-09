"""
build_televente_pool.py — Source unique Odoo pour le planning TELEVENTE (Vanessa).

Segment GMS "telephone-only" : magasins que le merchandiser physique (Gilles) ne
peut pas servir dans les temps (peu de references OU eloignes de Baillonville),
hors gros comptes lointains qui justifient le merch physique.

REGLE DE SEGMENTATION (Nicolas 09/06/2026) :
    Vanessa  =  n_refs <= 10  OU  (dist_km > 60  ET  n_refs < 20)
    Gilles   =  le reste (pools EXCLUSIFS)
    Exclus toujours : Arret, NoMerch.

CADENCE (principe Nicolas : la mediane historique est BIAISEE par les oublis,
donc on RESSERRE et on fait remonter les magasins deja en retard) :
    intervalle_cible = clamp(mediane_historique * RESSERREMENT, FLOOR, CEILING)
    1 seule commande (pas d'intervalle) -> DEMARRAGE_DEFAUT
    priorite = retard sur next_call_due (decroissant), puis avg_mois.

Lecture seule cote Odoo. Sortie : data/televente_pool_YYYY-MM-DD.{csv,md}.

Usage : python build_televente_pool.py [--target-date YYYY-MM-DD]
"""

import xmlrpc.client
import argparse
import csv
import re
import math
import statistics
from datetime import date, timedelta
from collections import defaultdict
from pathlib import Path

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"
BAILLON = (50.2904, 5.3387)  # Baillonville 5377

# --- Seuils de segmentation (Nicolas 09/06/2026) ---
REFS_MAX = 10        # <= 10 refs -> Vanessa (porte "petit assortiment")
DIST_MIN = 60        # > 60 km -> Vanessa (eloigne)
REFS_CARVEOUT = 20   # >= 20 refs : reste a Gilles meme si loin

# --- Cadence d'appel ---
RESSERREMENT = 0.75  # on appelle a 75% de l'intervalle historique observe
FLOOR = 14           # jamais plus serre que 14 j
CEILING = 35         # jamais plus espace que 35 j
DEMARRAGE_DEFAUT = 28  # cadence de demarrage si 1 seule commande 12m

GMS_PARENT_NAMES = ["Delhaize Le Lion", "Carrefour Belgium"]
GMS_NAME_TOKENS = ["Intermarch", "Spar ", "Spar-", " AD ", "AD Delhaize",
                   "Proxy Delhaize", "Affili", "Carrefour Market", "Carrefour Hyper",
                   "Hyper Carrefour", "Carrefour Express", "CARREFOUR MARKET", "Delhaize "]
NUMERIC_PREFIX_RE = re.compile(r"^\s*\d{4,}\s*[-_:.\s]*")


def is_gms(name, parent_name):
    if parent_name and any(c in parent_name for c in GMS_PARENT_NAMES):
        return True
    return any(tok in (name or "") for tok in GMS_NAME_TOKENS)


def clean_name(raw):
    if not raw:
        return ""
    return NUMERIC_PREFIX_RE.sub("", str(raw).strip()).strip()


def strip_html(s):
    if not s:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(s))).strip()


def haversine(a, b):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def load_geo():
    """Retourne (zip->coord, city_lower->coord) depuis GeoNames BE.txt."""
    zacc, cacc = defaultdict(list), defaultdict(list)
    path = Path(r"C:\Users\FlowUP\OneDrive\Teatower\data\geo\BE.txt")
    for line in path.open(encoding="utf-8"):
        c = line.split("\t")
        if len(c) < 11:
            continue
        try:
            pt = (float(c[9]), float(c[10]))
        except ValueError:
            continue
        zacc[c[1].strip()].append(pt)
        cacc[c[2].strip().lower()].append(pt)
    avg = lambda pts: (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
    return {z: avg(p) for z, p in zacc.items()}, {c: avg(p) for c, p in cacc.items()}


def distance_km(zip_code, city, zmap, cmap):
    z = (zip_code or "").strip()
    if z in zmap:
        return round(haversine(BAILLON, zmap[z])), "zip"
    c = (city or "").strip().lower()
    if c in cmap:
        return round(haversine(BAILLON, cmap[c])), "city"
    # zip texte type "Ciney" loge dans le champ city ? tente le zip comme nom de ville
    if z.lower() in cmap:
        return round(haversine(BAILLON, cmap[z.lower()])), "zip_as_city"
    return None, "none"


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-date", default=date.today().isoformat())
    ap.add_argument("--lookback-months", type=int, default=12)
    ap.add_argument("--out-dir", default=r"C:\Users\FlowUP\OneDrive\Teatower\data")
    args = ap.parse_args()
    today = date.fromisoformat(args.target_date)
    lookback = today - timedelta(days=30 * args.lookback_months)

    zmap, cmap = load_geo()
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    print(f"[*] Odoo uid={uid} | target={today} | geo:{len(zmap)} zips")

    sos = models.execute_kw(DB, uid, PASSWORD, "sale.order", "search_read",
        [[("state", "in", ["sale", "done"]), ("date_order", ">=", lookback.isoformat())]],
        {"fields": ["id", "partner_id", "partner_shipping_id", "date_order"]})
    pids = set()
    for s in sos:
        if s["partner_shipping_id"]:
            pids.add(s["partner_shipping_id"][0])
        if s["partner_id"]:
            pids.add(s["partner_id"][0])
    partners = models.execute_kw(DB, uid, PASSWORD, "res.partner", "read", [list(pids)],
        {"fields": ["id", "name", "parent_id", "street", "zip", "city",
                    "phone", "mobile", "email", "comment", "sale_warn"]})
    pmap = {p["id"]: p for p in partners}

    store_dates = defaultdict(list)
    so_to_store = {}
    for s in sos:
        ship = s["partner_shipping_id"][0] if s["partner_shipping_id"] else None
        bill = s["partner_id"][0] if s["partner_id"] else None
        store_pid = ship or bill
        p = pmap.get(store_pid, {})
        parent = p.get("parent_id")[1] if p.get("parent_id") else ""
        ok = is_gms(p.get("name"), parent)
        if not ok and bill:
            bp = pmap.get(bill, {})
            bparent = bp.get("parent_id")[1] if bp.get("parent_id") else ""
            ok = is_gms(bp.get("name"), bparent)
            if ok:
                store_pid = bill
                p = bp
        if not ok:
            continue
        store_dates[store_pid].append(date.fromisoformat(s["date_order"][:10]))
        so_to_store[s["id"]] = store_pid

    # lignes : refs distinctes + top produits (qty) par magasin
    so_ids = list(so_to_store.keys())
    lines = []
    for i in range(0, len(so_ids), 200):
        lines += models.execute_kw(DB, uid, PASSWORD, "sale.order.line", "search_read",
            [[("order_id", "in", so_ids[i:i + 200]), ("display_type", "=", False)]],
            {"fields": ["order_id", "product_id", "product_uom_qty", "price_subtotal"]})
    store_refs = defaultdict(set)
    store_prodqty = defaultdict(lambda: defaultdict(float))
    store_prodname = {}
    store_revenue = defaultdict(float)
    for l in lines:
        oid = l["order_id"][0] if l["order_id"] else None
        sp = so_to_store.get(oid)
        if not sp or not l.get("product_id"):
            continue
        prod_id, prod_name = l["product_id"][0], l["product_id"][1]
        store_refs[sp].add(prod_id)
        store_prodqty[sp][prod_id] += l.get("product_uom_qty") or 0.0
        store_revenue[sp] += l.get("price_subtotal") or 0.0
        store_prodname[prod_id] = clean_name(prod_name)

    rows = []
    for sp, dts in store_dates.items():
        p = pmap.get(sp, {})
        comment = p.get("comment") or ""
        arret = p.get("sale_warn") == "block" and "[ARRET" in str(comment)
        no_merch = "[NO-MERCH" in str(comment)
        if arret or no_merch:
            continue

        n_refs = len(store_refs.get(sp, set()))
        dist, dist_src = distance_km(p.get("zip"), p.get("city"), zmap, cmap)

        # --- segmentation Vanessa ---
        far = dist is not None and dist > DIST_MIN
        small = n_refs <= REFS_MAX
        is_vanessa = small or (far and n_refs < REFS_CARVEOUT)
        if not is_vanessa:
            continue
        if small and far:
            reason = "petit assortiment + eloigne"
        elif small:
            reason = "petit assortiment"
        else:
            reason = "eloigne"

        dts = sorted(dts)
        so_count = len(dts)
        last_order = dts[-1]
        days_since = (today - last_order).days
        intervals = [(dts[i] - dts[i - 1]).days for i in range(1, len(dts))]
        median_int = statistics.median(intervals) if intervals else None

        if median_int:
            target = int(clamp(round(median_int * RESSERREMENT), FLOOR, CEILING))
            cadence_src = "historique resserre"
        else:
            target = DEMARRAGE_DEFAUT
            cadence_src = "demarrage (1 cmd)"
        next_call = last_order + timedelta(days=target)
        overdue = (today - next_call).days  # >0 = en retard
        urgency = round(days_since / target, 2)

        # top produits habituels
        pq = store_prodqty.get(sp, {})
        top = sorted(pq.items(), key=lambda kv: -kv[1])[:8]
        top_products = "; ".join(f"{store_prodname.get(pid, pid)} (x{int(q)})" for pid, q in top)

        rows.append({
            "pid": sp,
            "magasin": clean_name(p.get("name")) or f"#{sp}",
            "zip": p.get("zip") or "", "city": p.get("city") or "",
            "street": p.get("street") or "",
            "phone": p.get("phone") or "", "mobile": p.get("mobile") or "",
            "email": p.get("email") or "",
            "dist_km": dist if dist is not None else "",
            "dist_src": dist_src,
            "n_refs": n_refs,
            "so_count_12m": so_count,
            "revenue_12m": round(store_revenue.get(sp, 0.0)),
            "avg_mois": round(store_revenue.get(sp, 0.0) / args.lookback_months),
            "last_order": last_order.isoformat(),
            "days_since": days_since,
            "median_interval": median_int if median_int is not None else "",
            "target_interval": target,
            "cadence_src": cadence_src,
            "next_call": next_call.isoformat(),
            "overdue_days": overdue,
            "urgency": urgency,
            "reason": reason,
            "top_products": top_products,
            "notes": strip_html(comment)[:300],
        })

    # tri : retard decroissant, puis avg_mois decroissant
    rows.sort(key=lambda r: (-r["overdue_days"], -r["avg_mois"]))

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = today.isoformat()
    csv_path = out / f"televente_pool_{stamp}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    overdue = [r for r in rows if r["overdue_days"] > 0]
    md_path = out / f"televente_pool_{stamp}.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# Pool Televente Vanessa — GMS (source Odoo, {stamp})\n\n")
        f.write(f"Regle : refs<={REFS_MAX} OU (dist>{DIST_MIN}km ET refs<{REFS_CARVEOUT}). "
                f"Cadence : mediane x{RESSERREMENT} clamp [{FLOOR},{CEILING}]j, demarrage {DEMARRAGE_DEFAUT}j.\n\n")
        f.write(f"- **Magasins pool Vanessa** : {len(rows)}\n")
        f.write(f"- **En retard (a appeler en priorite)** : {len(overdue)}\n")
        f.write(f"  - dont petit assortiment : {sum(1 for r in rows if 'petit' in r['reason'])}\n")
        f.write(f"  - dont eloigne : {sum(1 for r in rows if r['reason']=='eloigne')}\n\n")
        f.write("## File priorisee (retard decroissant)\n\n")
        f.write("| # | Retard | Urg | Magasin | km | refs | Derniere cmd | Cible | Tel | avg/mois | Motif |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(rows, 1):
            tel = r["phone"] or r["mobile"] or "—"
            rj = f"**{r['overdue_days']}j**" if r["overdue_days"] > 0 else f"{r['overdue_days']}j"
            f.write(f"| {i} | {rj} | {r['urgency']} | {r['magasin']} (#{r['pid']}) | "
                    f"{r['dist_km']} | {r['n_refs']} | {r['last_order']} ({r['days_since']}j) | "
                    f"{r['target_interval']}j | {tel} | {r['avg_mois']}€ | {r['reason']} |\n")

    print(f"[+] {len(rows)} magasins pool Vanessa | {len(overdue)} en retard")
    print(f"[+] CSV : {csv_path}")
    print(f"[+] MD  : {md_path}")
    # apercu console top 15
    print("\n-- TOP 15 file priorisee --")
    print(f"   {'retard':>6} {'urg':>4} {'km':>4} {'refs':>4} {'avg':>5}  magasin")
    for r in rows[:15]:
        print(f"   {r['overdue_days']:>5}j {r['urgency']:>4} {str(r['dist_km']):>4} "
              f"{r['n_refs']:>4} {r['avg_mois']:>4}€  {r['magasin'][:40]}")


if __name__ == "__main__":
    main()
