#!/usr/bin/env python3
"""
Rapport quotidien achats Teatower — 7h00 chaque matin.

- Analyse purchase.order + product.supplierinfo dans Odoo
- Détecte anomalies (prix, délais, retards, RFQ dormantes, factures manquantes)
- Met à jour automatiquement supplierinfo.price (si écart < 20%) et .delay (si écart >= 3j)
- Génère un rapport Markdown dans purchase/reports/YYYY-MM-DD.md
- Envoie l'email à nicolas.raes@teatower.com via mail.mail Odoo
- Commit + push auto

Usage :
  python scripts/purchase_daily_report.py              # exécution réelle
  python scripts/purchase_daily_report.py --dry-run    # pas d'écriture Odoo ni mail
"""
import argparse
import base64
import io
import datetime as dt
import pathlib
import statistics
import subprocess
import sys
import xmlrpc.client

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "purchase" / "reports"
LOG_PATH = ROOT / "purchase" / "LOG.md"

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"
EMAIL_TO = "nicolas.raes@teatower.com"

PRICE_VARIATION_REVIEW = 0.20   # > 20% = flag REVIEW, pas d'écriture auto
DELAY_THRESHOLD_DAYS = 3         # écart médian >= 3j = maj delay
RFQ_DORMANT_DAYS = 14
INVOICE_MISSING_DAYS = 30


def connect():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PWD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    def call(model, method, args, kw=None):
        return models.execute_kw(DB, uid, PWD, model, method, args, kw or {})
    return call


def fetch_data(call):
    today = dt.date.today()
    cutoff = (today - dt.timedelta(days=180)).isoformat()

    pos = call("purchase.order", "search_read",
               [[("date_order", ">=", cutoff),
                 ("state", "in", ["draft", "sent", "purchase", "done"])]],
               {"fields": ["id", "name", "partner_id", "state", "date_order",
                           "date_approve", "date_planned", "effective_date",
                           "amount_total", "invoice_status", "order_line"]})
    po_ids = [p["id"] for p in pos]

    lines = []
    if po_ids:
        lines = call("purchase.order.line", "search_read",
                     [[("order_id", "in", po_ids)]],
                     {"fields": ["id", "order_id", "product_id", "price_unit",
                                 "product_qty", "qty_received", "date_planned"]})

    sinfos = call("product.supplierinfo", "search_read",
                  [[]],
                  {"fields": ["id", "partner_id", "product_id", "product_tmpl_id",
                              "price", "delay", "date_end", "min_qty", "sequence"]})

    product_ids = list({l["product_id"][0] for l in lines if l.get("product_id")})
    product_map = {}
    if product_ids:
        prods = call("product.product", "search_read",
                     [[("id", "in", product_ids)]],
                     {"fields": ["id", "product_tmpl_id"]})
        product_map = {p["id"]: p["product_tmpl_id"][0] for p in prods if p.get("product_tmpl_id")}

    products_missing = call("product.template", "search_read",
                            [[("purchase_ok", "=", True),
                              ("type", "in", ["consu", "product"]),
                              ("seller_ids", "=", False),
                              ("active", "=", True)]],
                            {"fields": ["id", "name", "default_code"], "limit": 50})

    return pos, lines, sinfos, products_missing, product_map, today


def detect_anomalies(pos, lines, sinfos, products_missing, product_map, today):
    by_po = {p["id"]: p for p in pos}
    received_lines = [l for l in lines if l["qty_received"] and l["qty_received"] > 0]

    price_deltas = []
    sinfo_index = {}
    for s in sinfos:
        if s["partner_id"] and s["product_tmpl_id"]:
            key = (s["partner_id"][0], s["product_tmpl_id"][0])
            sinfo_index.setdefault(key, []).append(s)

    line_by_sinfo = {}
    for l in received_lines:
        po = by_po.get(l["order_id"][0])
        if not po or not po.get("partner_id") or not l.get("product_id"):
            continue
        partner_id = po["partner_id"][0]
        tmpl_id = product_map.get(l["product_id"][0])
        if tmpl_id is None:
            continue
        key = (partner_id, tmpl_id)
        line_by_sinfo.setdefault(key, []).append((po, l))

    price_updates, price_reviews = [], []
    delay_updates = []
    for key, entries in line_by_sinfo.items():
        sinfo_list = sinfo_index.get(key, [])
        if not sinfo_list:
            continue
        sinfo = sorted(sinfo_list, key=lambda s: s.get("sequence") or 10)[0]
        recent = sorted(entries, key=lambda e: e[0]["date_order"], reverse=True)[:5]

        prices = [e[1]["price_unit"] for e in recent if e[1]["price_unit"]]
        if prices and sinfo["price"]:
            median_price = statistics.median(prices)
            diff = abs(median_price - sinfo["price"]) / sinfo["price"] if sinfo["price"] else 0
            if abs(median_price - sinfo["price"]) >= 0.01 and diff > 0.001:
                record = {
                    "sinfo_id": sinfo["id"],
                    "partner": sinfo["partner_id"][1],
                    "product": (sinfo["product_id"] or sinfo["product_tmpl_id"])[1],
                    "old": sinfo["price"],
                    "new": round(median_price, 4),
                    "diff_pct": round(diff * 100, 1),
                }
                if diff > PRICE_VARIATION_REVIEW:
                    price_reviews.append(record)
                else:
                    price_updates.append(record)

        delays = []
        for po, _ in recent:
            if po.get("date_approve") and po.get("effective_date"):
                try:
                    d1 = dt.datetime.fromisoformat(po["date_approve"].replace(" ", "T"))
                    d2 = dt.datetime.fromisoformat(po["effective_date"].replace(" ", "T"))
                    delays.append((d2 - d1).days)
                except Exception:
                    pass
        if delays and sinfo.get("delay") is not None:
            median_delay = int(round(statistics.median(delays)))
            if abs(median_delay - sinfo["delay"]) >= DELAY_THRESHOLD_DAYS:
                delay_updates.append({
                    "sinfo_id": sinfo["id"],
                    "partner": sinfo["partner_id"][1],
                    "product": (sinfo["product_id"] or sinfo["product_tmpl_id"])[1],
                    "old": sinfo["delay"],
                    "new": median_delay,
                })

    late = []
    for l in lines:
        po = by_po.get(l["order_id"][0])
        if not po or po["state"] not in ("purchase", "done"):
            continue
        if l["qty_received"] is None or l["qty_received"] >= l["product_qty"]:
            continue
        if l.get("date_planned"):
            try:
                planned = dt.date.fromisoformat(l["date_planned"][:10])
                if planned < today:
                    late.append({
                        "po": po["name"],
                        "partner": po["partner_id"][1] if po["partner_id"] else "?",
                        "product": l["product_id"][1] if l["product_id"] else "?",
                        "days_late": (today - planned).days,
                        "qty_missing": l["product_qty"] - (l["qty_received"] or 0),
                    })
            except Exception:
                pass

    dormant = []
    for po in pos:
        if po["state"] not in ("draft", "sent"):
            continue
        try:
            d = dt.date.fromisoformat(po["date_order"][:10])
            age = (today - d).days
            if age > RFQ_DORMANT_DAYS:
                dormant.append({
                    "po": po["name"],
                    "partner": po["partner_id"][1] if po["partner_id"] else "?",
                    "age_days": age,
                    "amount": po["amount_total"],
                })
        except Exception:
            pass

    invoice_missing = []
    for po in pos:
        if po["state"] not in ("purchase", "done"):
            continue
        if po.get("invoice_status") != "to invoice":
            continue
        try:
            d = dt.date.fromisoformat(po["date_order"][:10])
            if (today - d).days > INVOICE_MISSING_DAYS:
                invoice_missing.append({
                    "po": po["name"],
                    "partner": po["partner_id"][1] if po["partner_id"] else "?",
                    "age_days": (today - d).days,
                    "amount": po["amount_total"],
                })
        except Exception:
            pass

    stale_sinfo = []
    for s in sinfos:
        if s.get("date_end"):
            try:
                if dt.date.fromisoformat(s["date_end"]) < today:
                    stale_sinfo.append(s)
                    continue
            except Exception:
                pass
        if (s.get("price") or 0) == 0:
            stale_sinfo.append(s)

    return {
        "price_updates": price_updates,
        "price_reviews": price_reviews,
        "delay_updates": delay_updates,
        "late": late,
        "dormant": dormant,
        "invoice_missing": invoice_missing,
        "stale_sinfo": stale_sinfo,
        "products_missing": products_missing,
        "pos_active": [p for p in pos if p["state"] in ("purchase", "done")],
    }


def apply_updates(call, anomalies, dry_run=False):
    if dry_run:
        return
    for u in anomalies["price_updates"]:
        call("product.supplierinfo", "write", [[u["sinfo_id"]], {"price": u["new"]}])
    for u in anomalies["delay_updates"]:
        call("product.supplierinfo", "write", [[u["sinfo_id"]], {"delay": u["new"]}])


def render_report(date, anomalies):
    md = [f"# Rapport achats — {date}", ""]
    po_active = anomalies["pos_active"]
    total = sum(p["amount_total"] for p in po_active)
    n_anom = (len(anomalies["price_reviews"]) + len(anomalies["late"])
              + len(anomalies["dormant"]) + len(anomalies["invoice_missing"])
              + len(anomalies["stale_sinfo"]) + len(anomalies["products_missing"]))
    md += ["## Résumé", "",
           f"- PO actives : **{len(po_active)}** (total **{total:,.0f} €**)",
           f"- Anomalies : **{n_anom}**",
           f"- Prix mis à jour : **{len(anomalies['price_updates'])}**",
           f"- Délais mis à jour : **{len(anomalies['delay_updates'])}**",
           ""]

    if anomalies["late"]:
        md += ["## 🔴 Commandes en retard", "",
               "| PO | Fournisseur | Produit | Retard (j) | Qté manquante |",
               "|---|---|---|---:|---:|"]
        for x in sorted(anomalies["late"], key=lambda r: -r["days_late"])[:30]:
            md.append(f"| {x['po']} | {x['partner']} | {x['product']} | {x['days_late']} | {x['qty_missing']:.0f} |")
        md.append("")

    if anomalies["price_reviews"]:
        md += ["## ⚠️ REVIEW — variation prix > 20% (non appliqué)", "",
               "| Produit | Fournisseur | Ancien | Nouveau | Écart % |",
               "|---|---|---:|---:|---:|"]
        for x in anomalies["price_reviews"]:
            md.append(f"| {x['product']} | {x['partner']} | {x['old']:.4f} | {x['new']:.4f} | {x['diff_pct']} |")
        md.append("")

    if anomalies["price_updates"]:
        md += ["## ✅ Prix fournisseur mis à jour", "",
               "| Produit | Fournisseur | Ancien | Nouveau | Écart % |",
               "|---|---|---:|---:|---:|"]
        for x in anomalies["price_updates"]:
            md.append(f"| {x['product']} | {x['partner']} | {x['old']:.4f} | {x['new']:.4f} | {x['diff_pct']} |")
        md.append("")

    if anomalies["delay_updates"]:
        md += ["## ✅ Délais fournisseur mis à jour", "",
               "| Produit | Fournisseur | delay avant (j) | delay après (j) |",
               "|---|---|---:|---:|"]
        for x in anomalies["delay_updates"]:
            md.append(f"| {x['product']} | {x['partner']} | {x['old']} | {x['new']} |")
        md.append("")

    if anomalies["dormant"]:
        md += [f"## 💤 RFQ dormantes (>{RFQ_DORMANT_DAYS} j)", "",
               "| PO | Fournisseur | Âge (j) | Montant |",
               "|---|---|---:|---:|"]
        for x in sorted(anomalies["dormant"], key=lambda r: -r["age_days"])[:30]:
            md.append(f"| {x['po']} | {x['partner']} | {x['age_days']} | {x['amount']:,.0f} € |")
        md.append("")

    if anomalies["invoice_missing"]:
        md += [f"## 🧾 Factures fournisseur manquantes (>{INVOICE_MISSING_DAYS} j)", "",
               "| PO | Fournisseur | Âge (j) | Montant |",
               "|---|---|---:|---:|"]
        for x in sorted(anomalies["invoice_missing"], key=lambda r: -r["age_days"])[:30]:
            md.append(f"| {x['po']} | {x['partner']} | {x['age_days']} | {x['amount']:,.0f} € |")
        md.append("")

    if anomalies["products_missing"]:
        md += ["## 📭 Produits sans fournisseur actif", "",
               "| Réf | Produit |", "|---|---|"]
        for p in anomalies["products_missing"][:30]:
            md.append(f"| {p.get('default_code') or '-'} | {p['name']} |")
        md.append("")

    if anomalies["stale_sinfo"]:
        md += [f"## 🗑️ Supplierinfo obsolètes ou prix=0 ({len(anomalies['stale_sinfo'])})", ""]
        for s in anomalies["stale_sinfo"][:20]:
            partner = s["partner_id"][1] if s.get("partner_id") else "?"
            prod = (s.get("product_id") or s.get("product_tmpl_id") or [None, "?"])[1]
            md.append(f"- {partner} · {prod} · price={s.get('price')} · date_end={s.get('date_end')}")
        md.append("")

    md += ["---", "🔗 [Odoo Achats](https://tea-tree.odoo.com/odoo/purchase)", ""]
    return "\n".join(md)


def md_to_html(md):
    html = ["<html><body style=\"font-family:Inter,Arial,sans-serif;color:#1a1d27\">"]
    for line in md.split("\n"):
        if line.startswith("# "):
            html.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            tag = "th" if html and html[-1].startswith("<table") else "td"
            if not html or not html[-1].startswith("<tr"):
                if not html[-1].startswith("<table"):
                    html.append("<table border=1 cellpadding=6 cellspacing=0 style=\"border-collapse:collapse\">")
            html.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
        elif line.startswith("- "):
            html.append(f"<li>{line[2:]}</li>")
        elif line.strip() == "---":
            html.append("<hr>")
        elif line.strip():
            html.append(f"<p>{line}</p>")
    html.append("</body></html>")
    out = "\n".join(html)
    out = out.replace("<p><table", "<table")
    return out


def send_email(call, date, md, html):
    attach_id = call("ir.attachment", "create", [[{
        "name": f"rapport_achats_{date}.md",
        "type": "binary",
        "datas": base64.b64encode(md.encode()).decode(),
        "mimetype": "text/markdown",
    }]])
    mail_id = call("mail.mail", "create", [[{
        "subject": f"Teatower — Rapport achats {date}",
        "body_html": html,
        "email_to": EMAIL_TO,
        "email_from": EMAIL_TO,
        "auto_delete": True,
        "attachment_ids": [(4, attach_id)],
    }]])
    call("mail.mail", "send", [[mail_id]])
    return mail_id


def git_push(report_path):
    try:
        subprocess.run(["git", "add", str(report_path), "purchase/LOG.md"], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m",
                        f"Rapport achats {dt.date.today().isoformat()}"],
                       cwd=ROOT, check=True)
        subprocess.run(["git", "push"], cwd=ROOT, check=True)
    except subprocess.CalledProcessError:
        pass


def append_log(date, anomalies, mail_id):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text("# Purchase agent — Log\n\n| Date | Anomalies | Prix maj | Délais maj | Mail |\n|---|---:|---:|---:|---|\n",
                            encoding="utf-8")
    n_anom = (len(anomalies["price_reviews"]) + len(anomalies["late"])
              + len(anomalies["dormant"]) + len(anomalies["invoice_missing"])
              + len(anomalies["stale_sinfo"]) + len(anomalies["products_missing"]))
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"| {date} | {n_anom} | {len(anomalies['price_updates'])} | {len(anomalies['delay_updates'])} | {mail_id or '-'} |\n")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    date = dt.date.today().isoformat()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    call = connect()
    pos, lines, sinfos, products_missing, product_map, today = fetch_data(call)
    anomalies = detect_anomalies(pos, lines, sinfos, products_missing, product_map, today)
    apply_updates(call, anomalies, dry_run=args.dry_run)

    md = render_report(date, anomalies)
    report_path = REPORTS_DIR / f"{date}.md"
    report_path.write_text(md, encoding="utf-8")

    mail_id = None
    if not args.dry_run:
        html = md_to_html(md)
        try:
            mail_id = send_email(call, date, md, html)
        except Exception as e:
            print(f"⚠️ email failed: {e}", file=sys.stderr)

    append_log(date, anomalies, mail_id)

    if not args.dry_run:
        git_push(report_path)

    n_anom = (len(anomalies["price_reviews"]) + len(anomalies["late"])
              + len(anomalies["dormant"]) + len(anomalies["invoice_missing"])
              + len(anomalies["stale_sinfo"]) + len(anomalies["products_missing"]))
    print(f"✓ Rapport {date} : {n_anom} anomalies, "
          f"{len(anomalies['price_updates'])} prix maj, "
          f"{len(anomalies['delay_updates'])} délais maj"
          + (f" — envoyé à {EMAIL_TO} (mail {mail_id})" if mail_id else ""))


if __name__ == "__main__":
    main()
