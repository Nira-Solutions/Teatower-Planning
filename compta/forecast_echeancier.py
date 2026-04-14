"""
Forecast échéancier Teatower — agent Compta.

Sources :
- Google Sheet Nicolas (onglets Échéancier + Budget Q1/Q2/Q3/Q4 2026)
- Odoo : account.move in_invoice non payées + historique fournisseurs récurrents

Sortie :
- Onglet "Forecast Odoo" dans le même Google Sheet :
  * Vue hebdo (WEEK XX) avec OUT prévus venant d'Odoo + Budget Qx prepaid
  * Comparaison avec l'Échéancier manuel de Nicolas → écart semaine par semaine
  * Détail ligne-à-ligne en bas (date, bénéficiaire, montant, source, référence)
"""

import argparse
import sys
import xmlrpc.client
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

# ─── Config ───────────────────────────────────────────────────────────────

SA_KEY = Path(__file__).parent / "google_service_account.json"
SHEET_ID = "1tpQQ5vTr5ekQesJKmkJi86cq9dG7sIFZ"
FORECAST_TAB = "Forecast Odoo"
ECHEANCIER_TAB = "Échéancier"
BUDGET_TABS = ["Budget Q1 2026", "Budget Q2 2026", "Budget Q3 2026", "Budget Q4 2026"]

ODOO_URL = "https://tea-tree.odoo.com"
ODOO_DB = "tsc-be-tea-tree-main-18515272"
ODOO_USER = "nicolas.raes@teatower.com"
ODOO_PWD = "Teatower123"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ─── Google Sheets ────────────────────────────────────────────────────────

def gs_client():
    if not SA_KEY.exists():
        sys.exit(f"❌ Clé service account introuvable : {SA_KEY}\n"
                 f"   Voir compta/SETUP_GOOGLE_SHEETS.md")
    creds = Credentials.from_service_account_file(str(SA_KEY), scopes=SCOPES)
    return gspread.authorize(creds)


def test_access():
    gc = gs_client()
    sh = gc.open_by_key(SHEET_ID)
    tabs = [ws.title for ws in sh.worksheets()]
    print(f"✓ Accès OK — {len(tabs)} onglets : {tabs}")
    return tabs


def read_echeancier_weeks(sh):
    """Extrait la structure semaine de l'onglet Échéancier : WEEK XX → total OUT manuel.
    Permet de comparer avec Odoo."""
    try:
        ws = sh.worksheet(ECHEANCIER_TAB)
    except gspread.WorksheetNotFound:
        return {}
    rows = ws.get_all_values()
    weeks = defaultdict(lambda: {"out": 0.0, "in": 0.0, "items": []})
    # Col A = libellé semaine, col G (~index 6) = OUT, col L (~index 11) = IN
    for r in rows:
        if not r or len(r) < 12:
            continue
        week_label = (r[0] or "").strip()
        if not week_label.upper().startswith("WEEK"):
            continue
        try:
            out = float((r[6] or "0").replace(",", ".").replace(" ", "").replace("€", ""))
        except ValueError:
            out = 0.0
        try:
            inv = float((r[11] or "0").replace(",", ".").replace(" ", "").replace("€", ""))
        except ValueError:
            inv = 0.0
        label = r[1] if len(r) > 1 else ""
        weeks[week_label]["out"] += out
        weeks[week_label]["in"] += inv
        if label and out:
            weeks[week_label]["items"].append((label, out))
    return dict(weeks)


def read_budget_prepaid(sh):
    """Extrait les lignes Budget Qx avec payment terms 'prepaid' — à anticiper."""
    prepaid = []
    for tab in BUDGET_TABS:
        try:
            ws = sh.worksheet(tab)
        except gspread.WorksheetNotFound:
            continue
        for row in ws.get_all_records():
            terms = str(row.get("Payement terms", "") or row.get("Payment terms", "")).lower()
            cost = row.get("Coût") or row.get("Cost") or 0
            try:
                cost = float(str(cost).replace(",", ".").replace(" ", ""))
            except (ValueError, TypeError):
                cost = 0.0
            if cost and "prepaid" in terms:
                prepaid.append({
                    "quarter": tab,
                    "type": row.get("Type", ""),
                    "fournisseur": row.get("Fournisseur", "") or row.get("détail", "") or row.get("detail", ""),
                    "montant": cost,
                    "detail": row.get("détail", "") or row.get("detail", ""),
                })
    return prepaid

# ─── Odoo ─────────────────────────────────────────────────────────────────

def odoo_call():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    m = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    def call(model, method, args, kw=None):
        return m.execute_kw(ODOO_DB, uid, ODOO_PWD, model, method, args, kw or {})
    return call


def read_odoo_dues(call):
    moves = call("account.move", "search_read", [[
        ("move_type", "=", "in_invoice"),
        ("state", "=", "posted"),
        ("payment_state", "in", ["not_paid", "partial", "in_payment"]),
    ]], {"fields": [
        "name", "partner_id", "invoice_date", "invoice_date_due",
        "amount_total", "amount_residual", "payment_state", "ref",
    ], "order": "invoice_date_due asc"})
    return moves


def detect_recurrents_odoo(call, months_back=6):
    since = (datetime.today() - timedelta(days=30 * months_back)).strftime("%Y-%m-%d")
    moves = call("account.move", "search_read", [[
        ("move_type", "=", "in_invoice"),
        ("state", "=", "posted"),
        ("invoice_date", ">=", since),
    ]], {"fields": ["partner_id", "invoice_date", "amount_total"]})

    by_partner = defaultdict(list)
    for m in moves:
        by_partner[m["partner_id"][0]].append(m)

    # Factures déjà ouvertes : ne pas doubler le récurrent si déjà présent dans dues
    recurrents = []
    for pid, ms in by_partner.items():
        if len(ms) < 3:
            continue
        dates = sorted(datetime.strptime(x["invoice_date"], "%Y-%m-%d") for x in ms)
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        avg_gap = sum(gaps) / len(gaps)
        if 25 <= avg_gap <= 35:
            freq, period_days = "mensuel", 30
        elif 80 <= avg_gap <= 100:
            freq, period_days = "trimestriel", 90
        else:
            continue
        avg_amount = sum(x["amount_total"] for x in ms) / len(ms)
        next_date = dates[-1] + timedelta(days=round(avg_gap))
        # Ne projeter que 1 ou 2 prochaines échéances (3 mois max)
        projections = []
        d = next_date
        for _ in range(3):
            if (d - datetime.today()).days > 90:
                break
            projections.append(d)
            d = d + timedelta(days=period_days)
        for d in projections:
            recurrents.append({
                "partner_id": pid,
                "partner_name": ms[0]["partner_id"][1],
                "avg_amount": round(avg_amount, 2),
                "frequence": freq,
                "next_date": d.strftime("%Y-%m-%d"),
            })
    return recurrents

# ─── Forecast builder ─────────────────────────────────────────────────────

def _try_date(s):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            pass
    return None


def week_label(dt):
    y, w, _ = dt.isocalendar()
    return f"WEEK {w}"


def build_rows(odoo_dues, odoo_recs, budget_prepaid):
    rows = []
    for m in odoo_dues:
        d = _try_date(m.get("invoice_date_due") or m.get("invoice_date"))
        if not d:
            continue
        rows.append({
            "date": d,
            "week": week_label(d),
            "beneficiaire": m["partner_id"][1] if m.get("partner_id") else "?",
            "montant": m.get("amount_residual", m.get("amount_total", 0)),
            "source": "Odoo — facture posted",
            "reference": m.get("name") or m.get("ref") or "",
            "statut": m.get("payment_state", ""),
        })
    for r in odoo_recs:
        d = _try_date(r["next_date"])
        rows.append({
            "date": d,
            "week": week_label(d),
            "beneficiaire": r["partner_name"],
            "montant": r["avg_amount"],
            "source": f"Odoo — récurrent {r['frequence']} projeté",
            "reference": "",
            "statut": "projeté",
        })
    # Budget prepaid : sans date précise, on les met tous au début du trimestre
    quarter_starts = {
        "Budget Q1 2026": datetime(2026, 1, 1),
        "Budget Q2 2026": datetime(2026, 4, 1),
        "Budget Q3 2026": datetime(2026, 7, 1),
        "Budget Q4 2026": datetime(2026, 10, 1),
    }
    for b in budget_prepaid:
        d = quarter_starts.get(b["quarter"])
        if not d or d < datetime.today() - timedelta(days=15):
            continue  # passé
        rows.append({
            "date": d,
            "week": week_label(d),
            "beneficiaire": b["fournisseur"] or b["detail"] or b["type"],
            "montant": b["montant"],
            "source": f"Budget {b['quarter'].replace('Budget ', '')} prepaid",
            "reference": b["detail"],
            "statut": "planifié",
        })
    rows.sort(key=lambda x: x["date"])
    return rows


def write_forecast(gc, rows, echeancier_weeks):
    sh = gc.open_by_key(SHEET_ID)
    try:
        ws = sh.worksheet(FORECAST_TAB)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=FORECAST_TAB, rows=max(len(rows)+60, 200), cols=10)

    now = datetime.today()

    # Agrégats par semaine
    by_week = defaultdict(lambda: {"total": 0.0, "items": []})
    for r in rows:
        by_week[r["week"]]["total"] += r["montant"]
        by_week[r["week"]]["items"].append(r)

    # Tri semaines par première date
    week_order = sorted(by_week.keys(),
                        key=lambda w: min(r["date"] for r in by_week[w]["items"]))

    # Totaux rapides
    j7 = sum(r["montant"] for r in rows if r["date"] <= now + timedelta(days=7))
    j30 = sum(r["montant"] for r in rows if r["date"] <= now + timedelta(days=30))
    total = sum(r["montant"] for r in rows)

    block = []
    block.append([f"Forecast Odoo — généré {now.strftime('%Y-%m-%d %H:%M')} ({len(rows)} lignes)"])
    block.append([f"À payer J+7 : {j7:,.2f} EUR   |   J+30 : {j30:,.2f} EUR   |   Total : {total:,.2f} EUR"])
    block.append([])

    # Vue hebdo + comparaison Échéancier manuel
    block.append(["VUE HEBDOMADAIRE (comparaison avec Échéancier manuel)"])
    block.append(["Semaine", "OUT Odoo prévu", "OUT Échéancier manuel", "Écart (Odoo - Manuel)", "Nb lignes Odoo"])
    for w in week_order:
        out_odoo = by_week[w]["total"]
        manual = echeancier_weeks.get(w, {}).get("out", 0.0)
        # l'échéancier manuel stocke les OUT en négatif
        manual_abs = abs(manual)
        ecart = out_odoo - manual_abs
        block.append([w,
                      f"{out_odoo:,.2f}",
                      f"{manual_abs:,.2f}" if manual_abs else "—",
                      f"{ecart:+,.2f}" if manual_abs else "n/a",
                      len(by_week[w]["items"])])
    block.append([])

    # Détail ligne à ligne
    block.append(["DÉTAIL LIGNE À LIGNE"])
    block.append(["Date échéance", "Semaine", "Bénéficiaire", "Montant", "Source", "Référence", "Statut"])
    for r in rows:
        block.append([
            r["date"].strftime("%Y-%m-%d"),
            r["week"],
            r["beneficiaire"],
            r["montant"],
            r["source"],
            r["reference"],
            r["statut"],
        ])

    ws.update("A1", block, value_input_option="USER_ENTERED")

    # Mise en forme minimale : bold headers, colonne montant format EUR
    ws.format("A1", {"textFormat": {"bold": True, "fontSize": 12}})
    ws.format("A4", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.98}})
    title_rows = [i+1 for i, r in enumerate(block) if r and isinstance(r[0], str) and r[0].startswith(("VUE", "DÉTAIL"))]
    for tr in title_rows:
        ws.format(f"A{tr}", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.98}})

    print(f"✓ '{FORECAST_TAB}' : {len(rows)} lignes · J+7 {j7:,.2f} · J+30 {j30:,.2f} · Total {total:,.2f}")

# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--test", action="store_true")
    args = p.parse_args()

    if args.test:
        test_access()
        return

    print("→ Lecture Google Sheet…")
    gc = gs_client()
    sh = gc.open_by_key(SHEET_ID)
    weeks = read_echeancier_weeks(sh)
    budget = read_budget_prepaid(sh)
    print(f"  Échéancier : {len(weeks)} semaines trackées")
    print(f"  Budget prepaid : {len(budget)} lignes")

    print("→ Lecture Odoo…")
    call = odoo_call()
    dues = read_odoo_dues(call)
    recs = detect_recurrents_odoo(call)
    print(f"  {len(dues)} factures fournisseurs ouvertes, {len(recs)} récurrents projetés")

    print("→ Génération…")
    rows = build_rows(dues, recs, budget)

    print("→ Écriture…")
    write_forecast(gc, rows, weeks)


if __name__ == "__main__":
    main()
