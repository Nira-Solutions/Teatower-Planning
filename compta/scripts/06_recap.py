"""Recap final : table des 22 SO/factures + totaux + Peppol."""
import xmlrpc.client, sys, io, json, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

SO_NAMES = ["S05473","S05463","S05472","S05459","S05471","S05474","S05470","S05404","S05480","S05457",
            "S05467","S05481","S05478","S05468","S05402","S05486","S05475","S05483","S05412","S05484",
            "S05485","S05476"]

sos = call("sale.order","search_read",[[("name","in",SO_NAMES)]],
           {"fields":["id","name","partner_id","partner_invoice_id","invoice_status","amount_to_invoice","invoice_ids"]})

rows = []
for s in sos:
    inv_ids = s.get("invoice_ids") or []
    invs = call("account.move","read",[inv_ids],
                {"fields":["id","name","state","amount_untaxed","amount_total","peppol_is_sent","peppol_move_state","peppol_message_uuid","invoice_date","partner_id"]}) if inv_ids else []
    # selectionner la derniere facture posted creee aujourd'hui
    invs_sorted = sorted(invs, key=lambda x: x["id"], reverse=True)
    last = next((i for i in invs_sorted if i.get("state")=="posted"), None)
    rows.append({
        "so": s["name"],
        "partner": s["partner_id"][1] if s.get("partner_id") else "",
        "invoice_partner_id": (s.get("partner_invoice_id") or [None])[0],
        "invoice_partner": (s.get("partner_invoice_id") or [None,""])[1],
        "amount_to_invoice_remaining": s.get("amount_to_invoice"),
        "invoice_status": s.get("invoice_status"),
        "invoice": last,
    })

# Sort by amount desc using last invoice total
rows.sort(key=lambda r: -(r["invoice"]["amount_total"] if r.get("invoice") else 0))

total_ht = sum((r["invoice"]["amount_untaxed"] if r.get("invoice") else 0) for r in rows)
total_ttc = sum((r["invoice"]["amount_total"] if r.get("invoice") else 0) for r in rows)
peppol_sent = sum(1 for r in rows if r.get("invoice") and r["invoice"].get("peppol_is_sent"))
peppol_processing = sum(1 for r in rows if r.get("invoice") and r["invoice"].get("peppol_move_state") in ("processing","ready","done"))
not_peppol = sum(1 for r in rows if r.get("invoice") and not r["invoice"].get("peppol_move_state"))

print(f"== RECAP ({len(rows)} SO) ==")
print(f"Total HT facture : {total_ht:.2f} EUR")
print(f"Total TTC facture: {total_ttc:.2f} EUR")
print(f"Peppol is_sent   : {peppol_sent}")
print(f"Peppol processing/ready/done : {peppol_processing}")
print(f"Email (no peppol): {not_peppol}\n")

print("| SO | Facture | Client (invoice partner) | HT | TTC | Statut SO | Peppol move_state | Peppol UUID |")
print("|---|---|---|---:|---:|---|---|---|")
for r in rows:
    inv = r.get("invoice") or {}
    print(f"| {r['so']} | {inv.get('name','-')} | {r['invoice_partner']} | {inv.get('amount_untaxed',0):.2f} | {inv.get('amount_total',0):.2f} | {r['invoice_status']} | {inv.get('peppol_move_state') or '-'} | {inv.get('peppol_message_uuid') or '-'} |")

# Save JSON
with open("compta/scripts/_recap.json","w",encoding="utf-8") as f:
    json.dump({"total_ht": total_ht, "total_ttc": total_ttc, "rows": rows}, f, indent=2, default=str)
