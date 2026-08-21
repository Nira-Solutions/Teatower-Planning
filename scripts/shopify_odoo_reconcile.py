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
  5. envoie un mail via Odoo si quoi que ce soit reste non resolu

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


def send_alert(odoo, subject, body):
    mail = odoo.x("mail.mail", "create", {
        "subject": subject,
        "body_html": "<pre style='font-family:monospace;font-size:13px'>" + body + "</pre>",
        "email_to": ALERT_TO,
        "auto_delete": False,
    })
    odoo.x("mail.mail", "send", [mail])


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

    problems = len(missing) + len(nosku) + len(failed)
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
