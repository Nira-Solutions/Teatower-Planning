"""
Forecast échéancier Teatower — agent Compta.

Lit :
- Google Sheet paiements de Nicolas (onglet récurrents manuels)
- Odoo : account.move in_invoice non payées + historique fournisseurs récurrents

Écrit :
- Onglet "Forecast" dans le même Google Sheet avec :
  * date d'échéance, bénéficiaire, montant, source, catégorie, statut
  * agrégats cash-out J+7 / J+30 / >30j
"""

import argparse
import json
import os
import sys
import xmlrpc.client
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

# ─── Config ───────────────────────────────────────────────────────────────

SA_KEY = Path(__file__).parent / "google_service_account.json"
SHEET_ID = "1tpQQ5vTr5ekQesJKmkJi86cq9dG7sIFZ"  # fichier paiements Nicolas
FORECAST_TAB = "Forecast"

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
    print(f"✓ Accès OK — {len(tabs)} onglets trouvés : {tabs}")
    return tabs


def read_recurrents(gc):
    """Lit l'onglet manuel de Nicolas pour capter les paiements récurrents
    hors Odoo (loyer, abonnements…). Détection souple : premier onglet,
    première table avec colonnes bénéficiaire/montant/fréquence."""
    sh = gc.open_by_key(SHEET_ID)
    for ws in sh.worksheets():
        if ws.title == FORECAST_TAB:
            continue
        rows = ws.get_all_records()
        if not rows:
            continue
        sample = rows[0]
        keys_lower = {k.lower(): k for k in sample.keys()}
        # heuristique : il faut au moins un libellé + montant
        if any("bénéf" in k or "benef" in k or "libell" in k or "fournisseur" in k
               for k in keys_lower) and any("montant" in k for k in keys_lower):
            return rows, ws.title
    return [], None

# ─── Odoo ─────────────────────────────────────────────────────────────────

def odoo_call():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    m = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    def call(model, method, args, kw=None):
        return m.execute_kw(ODOO_DB, uid, ODOO_PWD, model, method, args, kw or {})
    return call


def read_odoo_dues(call):
    """Factures fournisseurs non payées avec échéance."""
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
    """Détecte fournisseurs payés de façon récurrente (≥3 factures sur N mois
    avec intervalle régulier). Utile pour anticiper les prochaines échéances
    non encore facturées."""
    since = (datetime.today() - timedelta(days=30 * months_back)).strftime("%Y-%m-%d")
    moves = call("account.move", "search_read", [[
        ("move_type", "=", "in_invoice"),
        ("state", "=", "posted"),
        ("invoice_date", ">=", since),
    ]], {"fields": ["partner_id", "invoice_date", "amount_total"]})

    by_partner = defaultdict(list)
    for m in moves:
        by_partner[m["partner_id"][0]].append(m)

    recurrents = []
    for pid, ms in by_partner.items():
        if len(ms) < 3:
            continue
        dates = sorted([datetime.strptime(x["invoice_date"], "%Y-%m-%d") for x in ms])
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        avg_gap = sum(gaps) / len(gaps)
        if 25 <= avg_gap <= 35:  # mensuel
            freq = "mensuel"
        elif 80 <= avg_gap <= 100:  # trimestriel
            freq = "trimestriel"
        else:
            continue
        avg_amount = sum(x["amount_total"] for x in ms) / len(ms)
        next_date = dates[-1] + timedelta(days=round(avg_gap))
        recurrents.append({
            "partner_id": pid,
            "partner_name": ms[0].get("partner_id")[1] if ms[0].get("partner_id") else "?",
            "avg_amount": round(avg_amount, 2),
            "frequence": freq,
            "next_date": next_date.strftime("%Y-%m-%d"),
        })
    return recurrents

# ─── Forecast ─────────────────────────────────────────────────────────────

def build_forecast(odoo_dues, odoo_recurrents, manual_recurrents):
    rows = []
    for m in odoo_dues:
        rows.append({
            "date_echeance": m.get("invoice_date_due") or m.get("invoice_date"),
            "beneficiaire": m["partner_id"][1] if m.get("partner_id") else "?",
            "montant": m.get("amount_residual", m.get("amount_total", 0)),
            "source": "Odoo — facture posted",
            "reference": m.get("name") or m.get("ref") or "",
            "statut": m.get("payment_state", ""),
        })
    for r in odoo_recurrents:
        rows.append({
            "date_echeance": r["next_date"],
            "beneficiaire": r["partner_name"],
            "montant": r["avg_amount"],
            "source": f"Odoo — récurrent {r['frequence']} (projeté)",
            "reference": "",
            "statut": "projeté",
        })
    for r in manual_recurrents:
        keys_lower = {k.lower(): k for k in r.keys()}
        benef_key = next((keys_lower[k] for k in keys_lower
                          if "bénéf" in k or "benef" in k or "libell" in k or "fournisseur" in k), None)
        amount_key = next((keys_lower[k] for k in keys_lower if "montant" in k), None)
        date_key = next((keys_lower[k] for k in keys_lower if "date" in k or "écheance" in k or "echeance" in k), None)
        if not benef_key or not amount_key:
            continue
        rows.append({
            "date_echeance": r.get(date_key, "") if date_key else "",
            "beneficiaire": r[benef_key],
            "montant": r[amount_key],
            "source": "Manuel (sheet Nicolas)",
            "reference": "",
            "statut": "à payer",
        })
    rows.sort(key=lambda x: x["date_echeance"] or "9999")
    return rows


def write_forecast(gc, rows):
    sh = gc.open_by_key(SHEET_ID)
    try:
        ws = sh.worksheet(FORECAST_TAB)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=FORECAST_TAB, rows=max(len(rows)+20, 100), cols=8)

    today = datetime.today().strftime("%Y-%m-%d %H:%M")
    header = ["Date échéance", "Bénéficiaire", "Montant", "Source", "Référence", "Statut"]
    data = [[r["date_echeance"], r["beneficiaire"], r["montant"],
             r["source"], r["reference"], r["statut"]] for r in rows]

    # Agrégats
    now = datetime.today()
    total_j7 = sum(r["montant"] for r in rows
                   if r["date_echeance"] and _try_date(r["date_echeance"])
                   and _try_date(r["date_echeance"]) <= now + timedelta(days=7))
    total_j30 = sum(r["montant"] for r in rows
                    if r["date_echeance"] and _try_date(r["date_echeance"])
                    and _try_date(r["date_echeance"]) <= now + timedelta(days=30))
    total_all = sum(r["montant"] for r in rows)

    summary = [
        [f"Forecast généré {today} — {len(rows)} lignes"],
        [f"À payer J+7 : {total_j7:,.2f} EUR"],
        [f"À payer J+30 : {total_j30:,.2f} EUR"],
        [f"Total toutes échéances : {total_all:,.2f} EUR"],
        [""],
    ]

    ws.update("A1", summary + [header] + data, value_input_option="USER_ENTERED")
    print(f"✓ Onglet '{FORECAST_TAB}' mis à jour — {len(rows)} lignes, J+7 {total_j7:,.2f} EUR, J+30 {total_j30:,.2f} EUR")


def _try_date(s):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            pass
    return None

# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--test", action="store_true", help="Teste l'accès Sheets uniquement")
    args = p.parse_args()

    if args.test:
        test_access()
        return

    print("→ Lecture Google Sheet…")
    gc = gs_client()
    manual, tab = read_recurrents(gc)
    print(f"  {len(manual)} récurrents manuels depuis onglet '{tab}'")

    print("→ Lecture Odoo…")
    call = odoo_call()
    dues = read_odoo_dues(call)
    recs = detect_recurrents_odoo(call)
    print(f"  {len(dues)} factures fournisseurs ouvertes, {len(recs)} récurrents détectés")

    print("→ Génération forecast…")
    rows = build_forecast(dues, recs, manual)

    print("→ Écriture onglet Forecast…")
    write_forecast(gc, rows)


if __name__ == "__main__":
    main()
