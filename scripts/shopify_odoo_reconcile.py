#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconciliation Shopify <-> Odoo : garde-fou anti-commandes perdues.

CONTEXTE (21/08/2026)
---------------------
7 commandes payees (343,45 EUR) n'etaient jamais arrivees dans Odoo entre mai et
aout 2026, sans aucune alerte. Trois causes cumulees :
  1. variante Shopify sans SKU  -> le connecteur ne peut pas mapper la ligne
  2. produit Odoo inexistant    -> meme effet
  3. matrice de workflow incomplete (passerelle x statut) : toute commande
     arrivant deja Fulfilled/Partial (cheque cadeau auto-fulfill) echouait
Les trois sont corrigees, mais l'import reste pilote par webhook : un webhook
rate = commande perdue definitivement, sans trace. Ce script est le filet.

CE QU'IL FAIT
-------------
  1. compare les commandes Shopify des N derniers jours avec les sale.order Odoo
  2. reimporte automatiquement celles qui manquent (import_orders_by_remote_ids)
  3. signale les variantes Shopify ACTIVES sans SKU (prevention : detecte le
     probleme avant la premiere vente, pas apres)
  4. signale les lignes de file en echec cote Odoo
  5. signale les ateliers qui ne sont pas a 21% (la taxe de vente par defaut de
     la societe est le 6% du the : tout nouvel atelier naitra a 6% si personne
     ne corrige -- c'est exactement comme ca que l'ecart s'est installe)
  6. signale les ateliers marques "necessite une expedition" dans Shopify : un
     atelier ne s'expedie pas, sinon il part dans Sendcloud comme un colis a
     etiqueter et pollue la file (risque d'expedier un colis vide)
  7. signale les commandes bloquees dans Sendcloud sans etiquette depuis > 3 j
  8. signale les blocages Peppol : partenaires sans pays (la generation UBL
     BIS 3 echoue -- "Le pays est requis pour customer" -- et la facture ne
     part jamais) et factures restees en erreur d'envoi
  9. envoie un mail via Odoo si quoi que ce soit reste non resolu

Variables d'environnement requises :
    ODOO_PWD, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET, SHOPIFY_STORE

Usage :
    python scripts/shopify_odoo_reconcile.py            # verifie + repare + alerte
    python scripts/shopify_odoo_reconcile.py --dry-run  # verifie seulement
    python scripts/shopify_odoo_reconcile.py --days 60  # fenetre elargie
    python scripts/shopify_odoo_reconcile.py --no-mail  # pas d'alerte mail

Code retour : 0 = tout est aligne, 1 = anomalie persistante (a regarder).
"""
import argparse
import datetime
import os
import sys
import xmlrpc.client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_client import shopify  # noqa: E402

ODOO_URL = "https://tea-tree.odoo.com"
ODOO_DB = "tsc-be-tea-tree-main-18515272"
ODOO_USER = "nicolas.raes@teatower.com"
INSTANCE_ID = 1
ALERT_TO = "nicolas.raes@teatower.com"

# Un atelier est une prestation de service -> taux normal 21%, jamais le 6% du the.
CATEG_ATELIER = 103
TAUX_ATELIER = 21.0


class Odoo:
    def __init__(self):
        pwd = os.environ.get("ODOO_PWD")
        if not pwd:
            raise RuntimeError("ODOO_PWD absent de l'environnement")
        self.pwd = pwd
        common = xmlrpc.client.ServerProxy(ODOO_URL + "/xmlrpc/2/common")
        self.uid = common.authenticate(ODOO_DB, ODOO_USER, pwd, {})
        if not self.uid:
            raise RuntimeError("Authentification Odoo refusee")
        self.models = xmlrpc.client.ServerProxy(ODOO_URL + "/xmlrpc/2/object")

    def x(self, model, method, *args, **kw):
        return self.models.execute_kw(ODOO_DB, self.uid, self.pwd, model, method, list(args), kw)


def shopify_orders(days):
    """Toutes les commandes Shopify des N derniers jours (pagination since_id)."""
    since_date = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    orders, since_id = [], 0
    while True:
        batch = shopify.get("orders.json", params={
            "status": "any",
            "limit": 250,
            "since_id": since_id,
            "created_at_min": since_date + "T00:00:00+02:00",
        })["orders"]
        if not batch:
            break
        orders += batch
        since_id = max(o["id"] for o in batch)
        if len(batch) < 250:
            break
    return orders


def variants_without_sku():
    """Variantes de produits ACTIFS sans SKU -> toute commande les contenant sera perdue."""
    flagged, since_id = [], 0
    while True:
        batch = shopify.get("products.json", params={
            "limit": 250,
            "since_id": since_id,
            "fields": "id,title,status,variants",
        })["products"]
        if not batch:
            break
        for p in batch:
            if p.get("status") != "active":
                continue
            for v in p["variants"]:
                if not (v.get("sku") or "").strip():
                    flagged.append((p["title"], v["id"], v.get("title")))
        since_id = max(p["id"] for p in batch)
        if len(batch) < 250:
            break
    return flagged


def reimport(odoo, shopify_ids):
    """Reimporte des commandes par leur id Shopify, puis force le traitement de la file."""
    wiz = odoo.x("shopify.process.import.export", "create", {
        "shopify_instance_id": INSTANCE_ID,
        "shopify_operation": "import_orders_by_remote_ids",
        "shopify_order_ids": ",".join(shopify_ids),
    })
    odoo.x("shopify.process.import.export", "shopify_execute", [wiz])

    # les lignes creees restent en draft jusqu'au passage du cron (10 min) : on force
    lines = odoo.x("shopify.order.data.queue.line.ept", "search",
                   [["shopify_order_id", "in", list(shopify_ids)],
                    ["state", "in", ["draft", "failed"]]])
    if not lines:
        return []
    odoo.x("shopify.order.data.queue.line.ept", "write", lines, {"state": "draft"})
    for method in ("process_import_order_queue_data", "auto_import_order_queue_data"):
        try:
            odoo.x("shopify.order.data.queue.line.ept", method, lines)
        except Exception:
            pass  # le connecteur leve souvent apres avoir traite : on relit l'etat
    return odoo.x("shopify.order.data.queue.line.ept", "read", lines,
                  fields=["state", "shopify_order_id", "sale_order_id"])


def ateliers_hors_21(odoo):
    """Produits de la categorie Atelier dont la TVA n'est pas a 21%."""
    prods = odoo.x("product.template", "search_read",
                   [["categ_id", "=", CATEG_ATELIER]],
                   fields=["name", "default_code", "taxes_id"],
                   context={"active_test": False})
    taux = {t["id"]: t["amount"] for t in
            odoo.x("account.tax", "search_read", [["type_tax_use", "=", "sale"]],
                   fields=["amount"], context={"active_test": False})}
    hors = []
    for p in prods:
        rates = [taux.get(t) for t in p["taxes_id"]]
        if not rates or any(r != TAUX_ATELIER for r in rates):
            hors.append((p["id"], p["default_code"] or p["name"], rates))
    return hors


def ateliers_expedies():
    """Variantes d'atelier ACTIVES marquees requires_shipping -> pollueront Sendcloud."""
    prods = shopify.get("products.json",
                        params={"limit": 250, "fields": "id,title,status,variants"})["products"]
    items = []
    for p in prods:
        if "telier" not in p["title"] or p.get("status") != "active":
            continue
        for v in p["variants"]:
            items.append((v["inventory_item_id"], v.get("sku") or p["title"], v.get("title")))
    if not items:
        return []
    ids = ",".join(str(i[0]) for i in items)
    etat = {x["id"]: x.get("requires_shipping")
            for x in shopify.get("inventory_items.json",
                                 params={"ids": ids}).get("inventory_items", [])}
    return [(sku, vtitle) for iid, sku, vtitle in items if etat.get(iid) is not False]


def sendcloud_bloquees(jours=3):
    """Commandes importees dans Sendcloud, toujours sans etiquette apres N jours."""
    try:
        from sendcloud_client import sendcloud
    except Exception:
        return None  # credentials absents : controle ignore, pas une anomalie
    import unicodedata

    def norm(s):
        s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
        return " ".join(s.lower().split())

    parcels, cursor = [], None
    for _ in range(4):
        prm = {"limit": 100}
        if cursor:
            prm["cursor"] = cursor
        r = sendcloud.get("parcels", params=prm)
        parcels += r.get("parcels", [])
        nxt = r.get("next")
        if not nxt:
            break
        import urllib.parse
        cursor = urllib.parse.parse_qs(urllib.parse.urlparse(nxt).query).get("cursor", [None])[0]
    faits_num = {p.get("order_number") for p in parcels if p.get("order_number")}
    faits_nom = {norm(p.get("name")) for p in parcels}

    limite = (datetime.datetime.now() - datetime.timedelta(days=jours)).isoformat()
    bloquees = []
    for integ in sendcloud.get("integrations"):
        if integ.get("system") != "shopify_v2":
            continue
        for s in sendcloud.get("integrations/%s/shipments" % integ["id"],
                               params={"limit": 50}).get("results", []):
            num = s.get("order_number") or ""
            if num in faits_num or norm(s.get("name")) in faits_nom:
                continue
            if s.get("created_at", "")[:19] < limite[:19]:
                bloquees.append((num, s.get("created_at", "")[:16], s.get("name")))
    return bloquees


def peppol_bloques(odoo):
    """(partenaires Peppol sans pays, factures posted en erreur d'envoi Peppol)."""
    sans_pays = odoo.x("res.partner", "search_read",
                       [["peppol_endpoint", "!=", False], ["country_id", "=", False]],
                       fields=["display_name", "vat", "peppol_eas"])
    en_erreur = odoo.x("account.move", "search_read",
                       [["peppol_move_state", "=", "error"], ["state", "=", "posted"]],
                       fields=["name", "partner_id", "invoice_date", "amount_total"],
                       order="invoice_date desc")
    return sans_pays, en_erreur


def send_alert(odoo, subject, body):
    mail = odoo.x("mail.mail", "create", {
        "subject": subject,
        "body_html": "<pre style='font-family:monospace;font-size:13px'>" + body + "</pre>",
        "email_to": ALERT_TO,
        "auto_delete": False,
    })
    # mail.mail.send() renvoie None -> Fault "cannot marshal None" alors que le
    # mail est bien parti cote serveur. On avale ce Fault precis, sinon la tache
    # planifiee sort en erreur a chaque alerte (cf. reference_lettrage_ing_methode).
    try:
        odoo.x("mail.mail", "send", [mail])
    except xmlrpc.client.Fault as f:
        if "cannot marshal none" not in str(f.faultString).lower():
            raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30, help="fenetre de controle (defaut 30 jours)")
    ap.add_argument("--dry-run", action="store_true", help="detecte sans reparer")
    ap.add_argument("--no-mail", action="store_true", help="pas d'alerte mail")
    args = ap.parse_args()

    odoo = Odoo()
    out = []

    def say(line=""):
        print(line)
        out.append(line)

    stamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    say("Reconciliation Shopify <-> Odoo  --  " + stamp + "  (fenetre " + str(args.days) + " j)")
    say("=" * 72)

    sh = {str(o["id"]): o for o in shopify_orders(args.days)}
    known = {s["shopify_order_id"] for s in
             odoo.x("sale.order", "search_read", [["shopify_order_id", "!=", False]],
                    fields=["shopify_order_id"])}
    # une commande annulee dans Shopify n'a pas vocation a remonter
    missing = {k: o for k, o in sh.items() if k not in known and not o.get("cancelled_at")}

    say("Shopify : " + str(len(sh)) + " commandes   |   absentes d'Odoo : " + str(len(missing)))

    if missing:
        say()
        for k, o in sorted(missing.items(), key=lambda kv: kv[1]["created_at"]):
            say("  MANQUE  {:<9} {}  {:>8} EUR  ({}/{})".format(
                o["name"], o["created_at"][:16], o["total_price"],
                o["financial_status"], o.get("fulfillment_status") or "unshipped"))
        if not args.dry_run:
            say()
            say("  -> reimport en cours...")
            for res in reimport(odoo, list(missing)):
                so = res["sale_order_id"][1] if res["sale_order_id"] else "-"
                say("     {}  {:<8} {}".format(res["shopify_order_id"], res["state"], so))
            still = [k for k in missing
                     if not odoo.x("sale.order", "search_count", [["shopify_order_id", "=", k]])]
            missing = {k: missing[k] for k in still}
            say("  -> restant non resolu : " + str(len(missing)))

    nosku = variants_without_sku()
    say()
    say("Variantes actives sans SKU : " + str(len(nosku))
        + ("   (toute vente sur ces variantes sera perdue)" if nosku else ""))
    for title, vid, vtitle in nosku:
        say("  SANS SKU  {}  /  {}  (variant {})".format(title, vtitle, vid))

    failed = odoo.x("shopify.order.data.queue.line.ept", "search_read",
                    [["state", "=", "failed"]],
                    fields=["shopify_order_id", "create_date"], limit=50)
    say()
    say("Lignes de file en echec cote Odoo : " + str(len(failed)))
    for f in failed:
        say("  ECHEC  order {}  ({})".format(f["shopify_order_id"], f["create_date"][:16]))

    tva = ateliers_hors_21(odoo)
    say()
    say("Ateliers hors 21% : " + str(len(tva))
        + ("   (un atelier est une prestation de service)" if tva else ""))
    for pid, code, rates in tva:
        say("  TVA  {} ({}) -> {}".format(code, pid, rates or "aucune taxe"))

    exp = ateliers_expedies()
    say()
    say("Ateliers marques 'a expedier' : " + str(len(exp))
        + ("   (un atelier ne s'expedie pas)" if exp else ""))
    for sku, vtitle in exp:
        say("  EXPED  {}  /  {}".format(sku, vtitle))

    bloq = sendcloud_bloquees()
    say()
    if bloq is None:
        say("Sendcloud : controle ignore (credentials absents)")
        bloq = []
    else:
        say("Commandes sans etiquette Sendcloud depuis > 3 j : " + str(len(bloq)))
        for num, date, nom in bloq:
            say("  BLOQUE  {:<9} {}  {}".format(num, date, nom))

    sans_pays, pep_err = peppol_bloques(odoo)
    say()
    say("Peppol - partenaires sans pays : " + str(len(sans_pays))
        + ("   (leurs factures ne partiront pas)" if sans_pays else ""))
    for p in sans_pays:
        say("  PAYS  {} ({})  vat={}".format(p["display_name"], p["id"], p["vat"]))
    say("Peppol - factures en erreur d'envoi : " + str(len(pep_err)))
    for m in pep_err[:15]:
        say("  ERR   {:<18} {} {:>9.2f}  {}".format(
            m["name"], m["invoice_date"], m["amount_total"], m["partner_id"][1][:30]))

    problems = (len(missing) + len(nosku) + len(failed) + len(tva) + len(exp)
                + len(bloq) + len(sans_pays) + len(pep_err))
    say()
    say("=" * 72)
    say("RAS - tout est aligne." if not problems
        else str(problems) + " anomalie(s) a traiter.")

    if problems and not args.no_mail:
        send_alert(odoo, "[Shopify->Odoo] " + str(problems) + " anomalie(s) - " + stamp,
                   "\n".join(out))
        print("(alerte envoyee a " + ALERT_TO + ")")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
