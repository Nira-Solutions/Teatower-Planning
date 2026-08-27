# -*- coding: utf-8 -*-
"""
Commission Jerome Carlier -- Juillet 2026.

Volet 1 : croissance CA B2B, methode Option C figee le 04/05/2026
          (SO confirmees, tags canal + heritage parent, base HT).
Volet 2 : displays GMS poses en juillet -- proposition Odoo, la liste Adri
          reste la source officielle.
Volet 3 : nouveaux clients hors GMS dont la 1ere SO confirmee tombe en
          juillet et atteint 240 EUR HT.

Lecture seule.
"""
import os
import collections
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]

_c = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common")
UID = _c.authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return _m.execute_kw(DB, UID, PWD, model, method, args, kw or {})


# Tags canal retenus par l'Option C
TAGS_CANAL = [88, 27, 85, 28, 32, 84, 26, 31, 33]
TAGS_GMS = [88, 27]
TAGS_GROSSISTE = [32]

PALIERS = [(100, None), (80, 6000), (65, 4500), (50, 3200), (40, 2200),
           (31, 1500), (30, 1000), (25, 850), (20, 650), (15, 400), (10, 250)]


def palier(croissance):
    for seuil, montant in PALIERS:
        if croissance >= seuil:
            return seuil, montant
    return 0, 0


# --------------------------------------------------------------- partenaires
_cache = {}


def partner_info(pids):
    """id -> (nom, tags propres + tags du parent)."""
    manquants = [p for p in pids if p not in _cache]
    for i in range(0, len(manquants), 100):
        for p in call("res.partner", "read", [manquants[i:i + 100]],
                      {"fields": ["id", "name", "category_id", "parent_id"]}):
            _cache[p["id"]] = p
    # remonter les parents
    parents = [_cache[p]["parent_id"][0] for p in pids
               if _cache.get(p) and _cache[p]["parent_id"]
               and _cache[p]["parent_id"][0] not in _cache]
    for i in range(0, len(parents), 100):
        for p in call("res.partner", "read", [parents[i:i + 100]],
                      {"fields": ["id", "name", "category_id", "parent_id"]}):
            _cache[p["id"]] = p
    out = {}
    for pid in pids:
        p = _cache.get(pid)
        if not p:
            continue
        tags = set(p["category_id"] or [])
        if p["parent_id"]:
            par = _cache.get(p["parent_id"][0])
            if par:
                tags |= set(par["category_id"] or [])
        out[pid] = (p["name"] or "(sans nom #%d)" % pid, tags,
                    p["parent_id"][0] if p["parent_id"] else None)
    return out


def so_du_mois(d1, d2):
    """SO confirmees du mois, filtrees Option C."""
    sos = call("sale.order", "search_read",
               [[["state", "in", ["sale", "done"]],
                 ["date_order", ">=", d1 + " 00:00:00"],
                 ["date_order", "<=", d2 + " 23:59:59"]]],
               {"fields": ["name", "partner_id", "date_order", "amount_untaxed",
                           "user_id", "team_id"]})
    pids = list({s["partner_id"][0] for s in sos if s["partner_id"]})
    infos = partner_info(pids)
    retenues = []
    for s in sos:
        if not s["partner_id"]:
            continue
        nom, tags, _ = infos.get(s["partner_id"][0], ("?", set(), None))
        if tags & set(TAGS_CANAL):
            s["partner_nom"] = nom
            s["tags"] = tags
            retenues.append(s)
    return sos, retenues


def bloc(titre):
    print("\n" + "=" * 78)
    print(titre)
    print("=" * 78)


# ------------------------------------------------------- VOLET 1 CROISSANCE
bloc("VOLET 1 -- Croissance CA B2B  (Option C)")

periodes = {"2025": ("2025-07-01", "2025-07-31"), "2026": ("2026-07-01", "2026-07-31")}
res = {}
for an, (d1, d2) in periodes.items():
    tous, ret = so_du_mois(d1, d2)
    ca = sum(s["amount_untaxed"] for s in ret)
    res[an] = (tous, ret, ca)
    print("  juillet %s : %4d SO confirmees, %3d retenues Option C, CA HT %12s"
          % (an, len(tous), len(ret), format(round(ca), ",d").replace(",", " ")))

_, ret25, ca25 = res["2025"]
_, ret26, ca26 = res["2026"]
croiss = (ca26 / ca25 - 1) * 100 if ca25 else 0
seuil, montant = palier(croiss)
print("\n  Croissance brute : %+.2f %%  -> palier %s -> %s EUR"
      % (croiss, ("> 100" if seuil == 100 else "%d" % seuil) if seuil else "< 10",
         montant if montant is not None else "proratisation"))

# Controle des outliers des deux cotes (cf. arbitrage Tea Touch de juin)
for lib, lot, ca in (("juillet 2025", ret25, ca25), ("juillet 2026", ret26, ca26)):
    print("\n  Top 6 SO %s (poids dans le mois) :" % lib)
    for s in sorted(lot, key=lambda x: -x["amount_untaxed"])[:6]:
        print("    %-12s %-42s %10.2f  %5.1f %%"
              % (s["name"], s["partner_nom"][:42], s["amount_untaxed"],
                 s["amount_untaxed"] / ca * 100 if ca else 0))

# Meme calcul en excluant Tea Touch des deux cotes (comparabilite juin)
def sans(lot, motif):
    return [s for s in lot if motif.lower() not in s["partner_nom"].lower()]


ca25_st = sum(s["amount_untaxed"] for s in sans(ret25, "Tea Touch"))
ca26_st = sum(s["amount_untaxed"] for s in sans(ret26, "Tea Touch"))
if abs(ca25_st - ca25) > 1 or abs(ca26_st - ca26) > 1:
    c2 = (ca26_st / ca25_st - 1) * 100 if ca25_st else 0
    s2, m2 = palier(c2)
    print("\n  Hors Tea Touch : %s -> %s  = %+.2f %%  -> %s EUR"
          % (format(round(ca25_st), ",d").replace(",", " "),
             format(round(ca26_st), ",d").replace(",", " "), c2, m2))

# ------------------------------------------------------- VOLET 3 NOUVEAUX
bloc("VOLET 3 -- Nouveaux clients hors GMS (1ere SO confirmee >= 240 EUR HT)")

_, ret_juil, _ca26 = res["2026"]
candidats = []
for s in ret_juil:
    pid = s["partner_id"][0]
    nom, tags = s["partner_nom"], s["tags"]
    if tags & set(TAGS_GMS):
        continue
    candidats.append((pid, s))

pids = sorted({p for p, _ in candidats})
print("  %d partenaires hors GMS avec au moins une SO en juillet" % len(pids))

premieres = {}
for i in range(0, len(pids), 50):
    lot = pids[i:i + 50]
    for s in call("sale.order", "search_read",
                  [[["partner_id", "in", lot], ["state", "in", ["sale", "done"]]]],
                  {"fields": ["partner_id", "date_order", "name", "amount_untaxed"],
                   "order": "date_order asc"}):
        p = s["partner_id"][0]
        if p not in premieres:
            premieres[p] = s

nouveaux = []
for pid in pids:
    prem = premieres.get(pid)
    if not prem or not prem["date_order"].startswith("2026-07"):
        continue
    nom, tags, _ = partner_info([pid])[pid]
    cat = "Grossiste" if tags & set(TAGS_GROSSISTE) else "Horeca / Revendeur"
    taux = 130 if cat == "Grossiste" else 65
    nouveaux.append(dict(pid=pid, nom=nom, so=prem["name"],
                         date=prem["date_order"][:10],
                         montant=prem["amount_untaxed"],
                         cat=cat, commission=taux if prem["amount_untaxed"] >= 240 else 0))

print("\n  %-40s %-11s %-11s %10s %-18s %8s"
      % ("Client", "1ere SO", "Date", "HT", "Categorie", "Commis."))
for n in sorted(nouveaux, key=lambda x: -x["montant"]):
    print("  %-40s %-11s %-11s %10.2f %-18s %8s"
          % (n["nom"][:40], n["so"], n["date"], n["montant"], n["cat"],
             n["commission"] or "-- <240"))
eligibles = [n for n in nouveaux if n["commission"]]
print("\n  %d clients eligibles -> %d EUR"
      % (len(eligibles), sum(n["commission"] for n in eligibles)))

# ------------------------------------------------------- VOLET 2 DISPLAYS
bloc("VOLET 2 -- Displays GMS livres en juillet (proposition Odoo)")

prods = call("product.product", "search_read",
             [[["default_code", "in", ["M0005", "M0007"]]]],
             {"fields": ["id", "default_code", "name"]})
print("  Produits display :", [(p["default_code"], p["name"]) for p in prods])
pids_disp = [p["id"] for p in prods]

moves = call("stock.move", "search_read",
             [[["product_id", "in", pids_disp], ["state", "=", "done"],
               ["date", ">=", "2026-07-01"], ["date", "<=", "2026-07-31 23:59:59"]]],
             {"fields": ["partner_id", "product_id", "quantity", "date",
                         "reference", "picking_id", "location_dest_id"]})
par_client = collections.Counter()
for mv in moves:
    dest = (mv["location_dest_id"] or [0, ""])[1]
    if "Customers" not in dest and "Clients" not in dest:
        continue
    nom = (mv["partner_id"] or [0, "?"])[1]
    par_client[nom] += mv["quantity"]
print("  %d mouvements display sortants en juillet" % sum(par_client.values()))
for nom, q in par_client.most_common():
    print("    %-52s %.0f" % (nom[:52], q))
print("\n  Proposition : %d x 100 EUR = %d EUR"
      % (sum(par_client.values()), sum(par_client.values()) * 100))
print("  ATTENTION : la source officielle du volet 2 est la liste Adri.")
