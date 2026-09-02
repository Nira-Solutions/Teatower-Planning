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
import json
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
# Racine du depot : le nom d'utilisateur Windows differe d'un poste a l'autre
# (FlowUP sur le fixe, Nraes sur le portable) -> aucun chemin en dur.
REPO = Path(__file__).resolve().parent.parent

# --- Seuils de segmentation (Nicolas 09/06/2026) ---
REFS_MAX = 10        # <= 10 refs -> Vanessa (porte "petit assortiment")
DIST_MIN = 60        # > 60 km -> Vanessa (eloigne)
REFS_CARVEOUT = 20   # >= 20 refs : reste a Gilles meme si loin

# FORCE MERCH (Nicolas 10/06/2026) : gros clients que la regle distance/refs
# enverrait a tort en televente -> restent suivis physiquement par Gilles.
# Cle = pid Odoo (magasin + adresse de livraison). Exclus du pool Vanessa.
FORCE_MERCH_PIDS = {
    3016, 5649,   # KAIO Retail invest - Delhaize Ottignies (gros client, +1km au seuil)
    2914,         # Affilie 044725 - Delhaize Kraainem
    # 123144 Delhaize Ath : RETIRE le 02/09/2026. Le merch permanent decide le
    #        28/06 n'a jamais pu s'executer (seul magasin du pool en Hainaut
    #        occidental -> aucune tournee ne passe). 45j de retard, dernier
    #        passage 02/07 -> bascule en televente, cf. FORCE_TELEVENTE_PIDS.
    # Reseau pharmacies Condroz/Famenne bascule en suivi merchandiser (Nicolas 25/08/2026)
    3183,         # Pharmacie Tilman S.A. (6941 Bomal-sur-Ourthe)
    3181,         # Pharmacie Haulot-Bauche SRL (5330 Assesse)
    3182,         # Pharmacie TILMAN HAN SRL (5580 Han-sur-Lesse)
    3184,         # Ma Pharmacie de Baillonville (5377 Baillonville)
    114763,       # Lillodis SRL - Proxy Delhaize Lillois : le magasin ne veut PAS de suivi
                  # telephonique -> retour en visite merch (Nicolas 25/08/2026). Annule la
                  # decision 'APPEL ONLY' du 20/05/2026.
}
FORCE_MERCH_TOKENS = ["Delhaize Ottignies", "Delhaize Kraainem"]

# FORCE TELEVENTE (Nicolas 15/07/2026) : magasins que la regle refs/distance
# laisserait en merch mais que Nicolas bascule en suivi telephonique Vanessa.
# Ils entrent dans le pool Vanessa quelle que soit la segmentation -> et sortent
# donc automatiquement des visites Gilles (exclusivite, cf. build_planning_pool.py).
FORCE_TELEVENTE_PIDS = {
    2905,  # DEMARS S.A. - Carrefour Market Beauraing (Nicolas 15/07/2026)
    123144,  # Affilie 040490 - Delhaize Ath (Nicolas 02/09/2026) : bon client
             # (431 EUR/mois reel) mais isole en Hainaut occidental, jamais
             # visite depuis le 02/07 -> suivi telephonique Vanessa.
}

# PRIORITE (REGLES §13) : magasins a ne PAS louper. Ils remontent en tete de la
# file d'appels quel que soit leur retard, et portent un badge rouge sur la page.
# Cle = pid Odoo, valeur = motif affiche a Vanessa.
PRIORITE_PIDS = {
    123144: "bon client jamais visite depuis le 02/07 — ne pas louper",
}

# BASCULES AUTOMATIQUES (REGLES §14) : ecrites par check_couverture_gms.py.
# Un magasin CRITIQUE (> 45j sans contact) qui n'a PAS pu etre case dans le
# planning merch de la semaine bascule d'office ici -> il est appele. Pas de
# troisieme issue. FORCE_MERCH_PIDS prime : une decision explicite de Nicolas
# n'est jamais ecrasee par l'automatisme.
AUTO_TELEVENTE_FILE = REPO / "data" / "force_televente_auto.json"


def load_auto_televente():
    if not AUTO_TELEVENTE_FILE.exists():
        return {}
    try:
        raw = json.loads(AUTO_TELEVENTE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[!] {AUTO_TELEVENTE_FILE.name} illisible ({e}) -> ignore")
        return {}
    return {int(k): v for k, v in raw.items()}


AUTO_TELEVENTE = load_auto_televente()

# IMPLANTATION EN ATTENTE (REGLES §12) : magasins dont l'implantation PHYSIQUE est
# planifiee en merch mais pas encore executee. La commande d'ouverture existe deja,
# donc IMPL_AUTO_DAYS la prend a tort pour une implantation faite et declenche un
# suivi televente J+15 AVANT que le display soit pose -> double contact avec Gilles.
# Exclus du pool tant que l'implantation n'est pas faite ; des que le merch pose
# [IMPL date], retirer le pid d'ici : le magasin revient avec son suivi J+15 reel.
IMPL_PENDING_PIDS = {
    # 125070 Delhaize Warmonceau : implantation FAITE (visite merch du 09/07/2026),
    #        tag [IMPL 2026-07-09] pose le 17/08 -> retire d'ici, revient en pool
    #        televente (8 refs) avec son suivi J+15.
    126113,  # Affilie 42900 - Delhaize Esneux : nouveau client (cree 12/08/2026, SO du 12/08),
             # implantation Gilles S34 lundi 17/08 (demande Nicolas). Sans cette ligne le
             # magasin tombe en televente faute d'historique -> double contact avec Gilles.
}

# Override cadence d'appel (jours) par magasin -> prime sur la cadence calculee.
CADENCE_OVERRIDE_PID = {
    122944: 25,  # Lambertdis SRL - Spar Manhay : espacer les reassorts (Nicolas 10/06/2026)
}

# --- Cadence d'appel ---
RESSERREMENT = 0.75  # on appelle a 75% de l'intervalle historique observe
FLOOR = 14           # jamais plus serre que 14 j
CEILING = 35         # jamais plus espace que 35 j
DEMARRAGE_DEFAUT = 28  # cadence de demarrage si 1 seule commande 12m
SUIVI_IMPL_JOURS = 15  # suivi post-implantation : 1er appel a impl + 15j (pas 28)
IMPL_AUTO_DAYS = 75    # auto-detection implantation : 1ere SO d'un nouveau magasin
                       # (so_count==1) datant de <= 75j = implantation -> suivi J+15
                       # automatique, SANS tag manuel. Tag [IMPL date] = override.

GMS_PARENT_NAMES = ["Delhaize Le Lion", "Carrefour Belgium"]
GMS_NAME_TOKENS = ["Intermarch", "Spar ", "Spar-", " AD ", "AD Delhaize",
                   "Proxy Delhaize", "Affili", "Carrefour Market", "Carrefour Hyper",
                   "Hyper Carrefour", "Carrefour Express", "CARREFOUR MARKET", "Delhaize "]
NUMERIC_PREFIX_RE = re.compile(r"^\s*\d{4,}\s*[-_:.\s]*")
# Tag d'issue d'appel pose par Vanessa dans res.partner.comment :
#   [APPEL AAAA-MM-JJ REFUS]  -> refus de commander : reset cadence (revient a +cible)
#   [APPEL AAAA-MM-JJ NRP]    -> injoignable : reste du, retente S+1 (ne reset PAS)
APPEL_RE = re.compile(r"\[APPEL\s+(\d{4}-\d{2}-\d{2})\s+(REFUS|NRP)\]", re.IGNORECASE)
# Tag pose quand une IMPLANTATION est executee (merch) -> declenche le suivi
# televente J+15 :  [IMPL AAAA-MM-JJ]
IMPL_RE = re.compile(r"\[IMPL(?:ANTATION)?\s+(\d{4}-\d{2}-\d{2})\]", re.IGNORECASE)


def parse_impl(comment):
    """Date d'implantation la plus recente depuis les tags [IMPL ...], sinon None."""
    if not comment:
        return None
    text = re.sub(r"<[^>]+>", " ", str(comment))
    dates = []
    for m in IMPL_RE.finditer(text):
        try:
            dates.append(date.fromisoformat(m.group(1)))
        except ValueError:
            pass
    return max(dates) if dates else None


def parse_appels(comment):
    """Retourne (last_refus_date|None, last_nrp_date|None) depuis les tags [APPEL ...]."""
    last_refus, last_nrp = None, None
    if not comment:
        return last_refus, last_nrp
    text = re.sub(r"<[^>]+>", " ", str(comment))
    for m in APPEL_RE.finditer(text):
        try:
            d = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if m.group(2).upper() == "REFUS":
            if last_refus is None or d > last_refus:
                last_refus = d
        else:
            if last_nrp is None or d > last_nrp:
                last_nrp = d
    return last_refus, last_nrp


def is_gms(name, parent_name):
    # Comparaison INSENSIBLE A LA CASSE : les fiches Odoo sont saisies au petit
    # bonheur (« DELHAIZE BOONDAEL » en capitales ne matchait pas le token
    # « Delhaize  »). Le magasin basculait alors sur le pid de FACTURATION au
    # lieu du pid magasin -> pools merch et televente desalignes, exclusivite
    # cassee et bascule automatique sans effet (cf. REGLES §14, 02/09/2026).
    pn = (parent_name or "").casefold()
    nm = (name or "").casefold()
    if pn and any(c.casefold() in pn for c in GMS_PARENT_NAMES):
        return True
    return any(tok.casefold() in nm for tok in GMS_NAME_TOKENS)


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
    path = REPO / "data" / "geo" / "BE.txt"
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
    ap.add_argument("--out-dir", default=str(REPO / "data"))
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

    # contacts rattaches (res.partner enfants du magasin) -> personne de contact
    store_pids = list(store_dates.keys())
    contacts = []
    for i in range(0, len(store_pids), 200):
        contacts += models.execute_kw(DB, uid, PASSWORD, "res.partner", "search_read",
            [[("parent_id", "in", store_pids[i:i + 200])]],
            {"fields": ["parent_id", "name", "function", "phone", "mobile", "email", "type"]})
    store_contacts = defaultdict(list)
    for c in contacts:
        if c.get("parent_id"):
            store_contacts[c["parent_id"][0]].append(c)

    def best_contact(sp, fallback):
        """Meilleur contact : priorite a celui qui a une fonction, puis un tel."""
        cs = store_contacts.get(sp, [])
        cs = [c for c in cs if (c.get("name") or "").strip()]
        if not cs:
            return {"name": "", "function": "",
                    "phone": fallback.get("phone") or fallback.get("mobile") or "",
                    "email": fallback.get("email") or ""}
        cs.sort(key=lambda c: (0 if c.get("function") else 1,
                               0 if (c.get("phone") or c.get("mobile")) else 1))
        c = cs[0]
        return {"name": clean_name(c.get("name")), "function": c.get("function") or "",
                "phone": c.get("phone") or c.get("mobile") or fallback.get("phone") or "",
                "email": c.get("email") or fallback.get("email") or ""}

    rows = []
    for sp, dts in store_dates.items():
        p = pmap.get(sp, {})
        comment = p.get("comment") or ""
        arret = p.get("sale_warn") == "block" and "[ARRET" in str(comment)
        no_merch = "[NO-MERCH" in str(comment)
        if arret or no_merch:
            continue
        # Force merch : gros clients gardes pour Gilles (jamais en televente)
        pname = p.get("name") or ""
        if sp in FORCE_MERCH_PIDS or any(t in pname for t in FORCE_MERCH_TOKENS):
            continue
        # Implantation physique pas encore faite -> reste merch, pas d'appel
        if sp in IMPL_PENDING_PIDS and not parse_impl(comment):
            continue

        n_refs = len(store_refs.get(sp, set()))
        dist, dist_src = distance_km(p.get("zip"), p.get("city"), zmap, cmap)

        # --- segmentation Vanessa ---
        far = dist is not None and dist > DIST_MIN
        small = n_refs <= REFS_MAX
        auto = AUTO_TELEVENTE.get(sp)
        forced = sp in FORCE_TELEVENTE_PIDS or auto is not None
        is_vanessa = forced or small or (far and n_refs < REFS_CARVEOUT)
        if not is_vanessa:
            continue
        if auto:
            reason = f"bascule auto — {auto.get('motif', 'sans visite')}"
        elif forced:
            reason = "bascule televente (decision Nicolas)"
        elif small and far:
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

        # Override cadence par magasin (prime sur le calcul)
        if sp in CADENCE_OVERRIDE_PID:
            target = CADENCE_OVERRIDE_PID[sp]
            cadence_src = "override magasin"

        # Issues d'appel (tags Odoo). Un REFUS recale la cadence (le client a ete
        # touche, il revient a sa prochaine echeance) ; un NRP ne recale PAS
        # (toujours du, a retenter S+1) mais on le memorise.
        last_refus, last_nrp = parse_appels(comment)
        anchor = max([d for d in (last_order, last_refus) if d is not None])
        next_call = anchor + timedelta(days=target)
        cadence_src_eff = cadence_src

        # SUIVI POST-IMPLANTATION : si une implantation a eu lieu et qu'aucun
        # suivi televente n'a encore ete fait apres (pas de REFUS/NRP apres l'impl,
        # pas de commande > impl+3j = au-dela de la cmd d'implant), on cale le 1er
        # appel a impl + 15j (au lieu de 28) pour un suivi rapproche.
        # impl_date = tag [IMPL date] explicite, SINON auto-detecte = 1ere SO d'un
        # nouveau magasin (so_count==1) datant de <= IMPL_AUTO_DAYS (= implantation).
        impl_date = parse_impl(comment)
        impl_auto = False
        if impl_date is None and so_count == 1 and (today - dts[0]).days <= IMPL_AUTO_DAYS:
            impl_date = dts[0]
            impl_auto = True
        suivi_impl = False
        if impl_date:
            post = False
            if last_refus and last_refus > impl_date:
                post = True
            if last_nrp and last_nrp > impl_date:
                post = True
            if last_order > impl_date + timedelta(days=3):
                post = True
            if not post:
                suivi_impl = True
                next_call = impl_date + timedelta(days=SUIVI_IMPL_JOURS)
                cadence_src_eff = "suivi implantation J+15"

        overdue = (today - next_call).days  # >0 = en retard
        urgency = round((today - anchor).days / target, 2)
        ct = best_contact(sp, p)

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
            "contact_name": ct["name"], "contact_function": ct["function"],
            "contact_phone": ct["phone"], "contact_email": ct["email"],
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
            "cadence_src": cadence_src_eff,
            "next_call": next_call.isoformat(),
            "overdue_days": overdue,
            "urgency": urgency,
            "last_refus": last_refus.isoformat() if last_refus else "",
            "last_nrp": last_nrp.isoformat() if last_nrp else "",
            "impl_date": impl_date.isoformat() if impl_date else "",
            "suivi_impl": "1" if suivi_impl else "",
            "reason": reason,
            # une bascule auto est prioritaire d'office : le magasin a deja
            # ete oublie une fois, il ne doit pas l'etre deux.
            "priorite": PRIORITE_PIDS.get(sp, "") or (
                auto.get("motif", "") if auto else ""),
            "top_products": top_products,
            "notes": strip_html(comment)[:300],
        })

    # tri : prioritaires d'abord, puis retard decroissant, puis avg_mois decroissant
    rows.sort(key=lambda r: (0 if r["priorite"] else 1, -r["overdue_days"], -r["avg_mois"]))

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
