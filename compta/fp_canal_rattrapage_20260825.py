# -*- coding: utf-8 -*-
"""
RATTRAPAGE CLASSIFICATION CANAL (position fiscale) - 25/08/2026

Demande Nicolas : "occupe toi de bien classer les clients pour le compte de
resultats car j'ai vu des clients ou des commandes qui n'etaient pas en gms ou
revendeurs".

Mecanique (cf project_canal_gms_fp_fix) : le canal du P&L est porte par le COMPTE
DE PRODUIT, qui vient de la POSITION FISCALE.
  FP 6 GMS -> 700600 | FP 7 Horeca -> 700300 | FP 8 Revendeurs -> 700500
  FP 35 Institutions -> 700700
Sans FP canal, Odoo auto-applique FP 1 "Belgium B2B" qui ne mappe rien -> le CA
tombe dans le fourre-tout 700000.

Ce script fait DEUX choses, toutes deux sans impact TVA (aucune FP canal n'a de
tax map) et sans impact resultat (presentation seulement) :

  ETAPE 1 - res.partner : pose la FP canal deduite des tags, UNIQUEMENT si
            - la fiche porte un seul canal (tags non contradictoires),
            - is_company OU vat renseigne (garde-fou particuliers Shopify,
              cf feedback_fp_canal_garde_fou_particuliers),
            - la FP actuelle est VIDE ou "Belgium B2B" (id 1). On ne touche
              JAMAIS une FP existante (Intra-Community, OSS...) : ecraser une FP
              a enjeu TVA serait une faute.

  ETAPE 2 - sale.order encore non facturees : realigne fiscal_position_id sur la
            FP du partenaire. C'est LA fuite : une SO encodee avant la correction
            de la fiche garde "Belgium B2B" et sa facture retombe en 700000.

Le reclassement de l'HISTORIQUE deja facture (700000 -> 700x00) n'est PAS fait
ici : ecriture comptable = accord explicite de Nicolas
(cf feedback_compta_no_pl_changes_without_approval).

Usage : python fp_canal_rattrapage_20260825.py            (DRY-RUN)
        python fp_canal_rattrapage_20260825.py --apply
"""
import os, sys, json, collections
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
if not PWD:
    raise SystemExit("Definir ODOO_PWD avant d'executer.")
uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(mo, me, a, k=None):
    return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

DRY = "--apply" not in sys.argv
print(f"MODE: {'DRY-RUN (rien ecrit)' if DRY else 'APPLY (ecriture reelle)'}\n")

TAG2FP = {27: 6, 88: 6,               # GMS / Canal GMS
          26: 7, 84: 7, 31: 7, 33: 7, # HoReCA / Canal Horeca / Horeca Vrac & infu / Horeca VIA Grossiste
          28: 8, 81: 8,               # Revendeur / rev
          29: 35, 30: 35}             # Institution / Institution TT
FPNAME = {6: "GMS", 7: "Horeca", 8: "Revendeurs", 35: "Institutions"}
FP_NEUTRES = {None, 1}   # vide ou "Belgium B2B" : ne mappent rien -> ecrasables
tags = {t["id"]: t["name"] for t in call("res.partner.category", "search_read", [[]], {"fields": ["name"]})}

rollback = {"partners": [], "orders": []}

# =====================================================================
# ETAPE 1 : position fiscale sur les fiches partenaires
# =====================================================================
print("=" * 100)
print("ETAPE 1 - res.partner : FP canal deduite des tags")
print("=" * 100)
ps = call("res.partner", "search_read",
          [[["category_id", "in", list(TAG2FP)], ["active", "=", True]]],
          {"fields": ["id", "name", "category_id", "property_account_position_id",
                      "is_company", "vat"], "limit": 5000})
print(f"{len(ps)} fiches portant au moins un tag canal")

need, conflict, skipped = [], [], []
for p in ps:
    want = {TAG2FP[t] for t in p["category_id"] if t in TAG2FP}
    cur = p.get("property_account_position_id")
    curid = cur[0] if cur else None
    if curid in want:
        continue
    if curid not in FP_NEUTRES:
        conflict.append((p, want, cur))
        continue
    if len(want) != 1:
        skipped.append((p, want, "tags canal contradictoires"))
        continue
    if not (p.get("is_company") or p.get("vat")):
        skipped.append((p, want, "ni is_company ni TVA (garde-fou particuliers)"))
        continue
    need.append((p, list(want)[0]))

cnt = collections.Counter(FPNAME[fp] for _, fp in need)
print(f"\nA APPLIQUER : {len(need)} fiches  {dict(cnt)}")
for p, fp in sorted(need, key=lambda x: (FPNAME[x[1]], (x[0]["name"] or ""))):
    nm = (p["name"] or f"(sans nom #{p['id']})")[:44]
    print(f"  #{p['id']:<7} {nm:44} -> {FPNAME[fp]:12} tags={[tags.get(t) for t in p['category_id']]}")
    if not DRY:
        rollback["partners"].append({"id": p["id"], "old": p.get("property_account_position_id") or False})
        call("res.partner", "write", [[p["id"]], {"property_account_position_id": fp}])

print(f"\nCONFLITS (FP non neutre deja posee) : {len(conflict)} -- NON modifies, a arbitrer")
for p, want, cur in conflict:
    nm = (p["name"] or f"(sans nom #{p['id']})")[:40]
    print(f"  #{p['id']:<7} {nm:40} FP={cur[1][:16]:18} tags={[tags.get(t) for t in p['category_id']]}")

print(f"\nECARTES : {len(skipped)}")
for p, want, why in skipped:
    nm = (p["name"] or f"(sans nom #{p['id']})")[:40]
    print(f"  #{p['id']:<7} {nm:40} ({why}) tags={[tags.get(t) for t in p['category_id']]}")

# =====================================================================
# ETAPE 2 : realignement des sale.order non facturees
# =====================================================================
print()
print("=" * 100)
print("ETAPE 2 - sale.order non facturees : fiscal_position_id <- FP du partenaire")
print("=" * 100)
sos = call("sale.order", "search_read",
           [[["state", "in", ["draft", "sent", "sale"]], ["invoice_status", "!=", "invoiced"]]],
           {"fields": ["name", "partner_id", "fiscal_position_id", "state",
                       "invoice_status", "amount_total"], "limit": 2000})
pids = sorted({s["partner_id"][0] for s in sos})
pd = {p["id"]: p for p in call("res.partner", "read", [pids],
                               {"fields": ["name", "property_account_position_id"]})}
bad, so_tax = [], []
for s in sos:
    pfp = pd[s["partner_id"][0]].get("property_account_position_id")
    if not pfp or pfp[0] not in FPNAME:
        continue                                   # pas de canal cote fiche -> rien a propager
    sfp = s.get("fiscal_position_id")
    if sfp and sfp[0] == pfp[0]:
        continue
    # Meme garde-fou qu'a l'etape 1 : on n'ecrase que du VIDE ou du "Belgium B2B".
    # Une SO en OSS B2C France / EU B2C porte un enjeu TVA -> on la signale, on n'y touche pas.
    if sfp and sfp[0] not in FP_NEUTRES:
        so_tax.append((s, pfp, sfp))
        continue
    bad.append((s, pfp, sfp))

print(f"{len(bad)} commandes a realigner")
for s, pfp, sfp in sorted(bad, key=lambda x: -x[0]["amount_total"]):
    print(f"  {s['name']:9} {s['state']:6} {s['invoice_status']:12} {s['amount_total']:>9,.2f} "
          f"{s['partner_id'][1][:32]:32} {str(sfp and sfp[1])[:14]:15} -> {pfp[1]}")
    if not DRY:
        rollback["orders"].append({"id": s["id"], "name": s["name"], "old": sfp or False})
        call("sale.order", "write", [[s["id"]], {"fiscal_position_id": pfp[0]}])

print()
print(f"{len(so_tax)} commandes NON touchees (FP a enjeu TVA) -- a arbitrer :")
for s, pfp, sfp in so_tax:
    print(f"  {s['name']:9} {s['state']:6} {s['invoice_status']:12} {s['amount_total']:>9,.2f} "
          f"{s['partner_id'][1][:32]:32} {sfp[1][:16]:18} (fiche = {pfp[1]})")

if not DRY:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_rollback_fp_20260825.json")
    json.dump(rollback, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nRollback ecrit : {path}")

print("\nRAPPEL : aucune ecriture comptable. L'historique deja facture en 700000 "
      "reste tel quel (reclassement = accord Nicolas).")
