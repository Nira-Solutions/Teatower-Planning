"""
Récupère pour chaque magasin déjà planifié S22 (mardi 26/05 + mercredi 27/05) :
  - last_so_date (max date_order sur sale.order state in ['sale','done']
                  où partner_id = pid OR partner_shipping_id = pid
                  OR commercial_partner_id = pid)
  - last_so_name, last_so_amount_total
  - ancienneté en jours par rapport à 2026-05-21 (target date Nicolas)
  - alerte si < 14 jours = revisite trop rapprochée (règle 14-21j Tier B/C)

Source maître : sale.order Odoo. PAS les fichiers planning .md/.html.
"""

import xmlrpc.client
from datetime import date

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"

TODAY = date(2026, 5, 21)

# Liste des partners planifiés S22 — IDs Odoo (ship + commercial)
TARGETS = [
    # Mardi 26/05
    {"label": "Delhaize Fragnée (GIMALEX)", "pid_ship": 5580, "pid_invoice": 2965, "day": "Ma 26/05"},
    {"label": "Delhaize Barchon (BARCHONEW)", "pid_ship": 119815, "pid_invoice": 119815, "day": "Ma 26/05"},
    {"label": "Intermarché Herve (LEHDIS)", "pid_ship": 120491, "pid_invoice": 120491, "day": "Ma 26/05"},
    {"label": "Hyper Carrefour Fleron", "pid_ship": 7760, "pid_invoice": 7760, "day": "Ma 26/05"},
    # Mercredi 27/05
    {"label": "Delhaize Recogne / Libramont", "pid_ship": 122091, "pid_invoice": 122091, "day": "Me 27/05"},
    {"label": "Delhaize Bertrix", "pid_ship": 123303, "pid_invoice": 123303, "day": "Me 27/05"},
    {"label": "CM Bastogne CC Port (Orkari)", "pid_ship": 123189, "pid_invoice": 123189, "day": "Me 27/05"},
    {"label": "AD Delhaize Bastogne (SA Marer)", "pid_ship": 8558, "pid_invoice": 8558, "day": "Me 27/05"},
]


def main():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    print(f"[*] Odoo uid={uid} | today={TODAY}\n")

    print(f"{'Day':<8} {'#PID':<8} {'Magasin':<35} {'Dern. SO':<10} {'Anc.':<6} {'Montant':<10} {'SO name'}")
    print("-" * 110)

    results = []
    for t in TARGETS:
        # On cherche sur partner_id OR partner_shipping_id, mais
        # on inclut aussi commercial_partner_id pour capter le cas
        # "Carrefour Belgium intégré" où le shipping = magasin mais
        # le partner_id = central Carrefour.
        candidates = list({t["pid_ship"], t["pid_invoice"]})
        domain = ["&",
                  ("state", "in", ["sale", "done"]),
                  "|", "|",
                  ("partner_shipping_id", "in", candidates),
                  ("partner_id", "in", candidates),
                  ("partner_invoice_id", "in", candidates),
                  ]
        sos = models.execute_kw(
            DB, uid, PASSWORD,
            "sale.order", "search_read",
            [domain],
            {"fields": ["id", "name", "date_order", "amount_total",
                        "partner_id", "partner_shipping_id"],
             "order": "date_order desc",
             "limit": 5}
        )
        if not sos:
            last_date_iso = "Jamais"
            anc = "-"
            total = "-"
            soname = "—"
        else:
            top = sos[0]
            d = top["date_order"][:10]
            last_date_iso = d
            anc = f"{(TODAY - date.fromisoformat(d)).days}j"
            total = f"{top['amount_total']:.2f} €"
            soname = top["name"]

        print(f"{t['day']:<8} #{t['pid_ship']:<7} {t['label'][:33]:<35} {last_date_iso:<10} {anc:<6} {total:<10} {soname}")
        results.append({
            "day": t["day"],
            "pid": t["pid_ship"],
            "label": t["label"],
            "last_so_date": last_date_iso,
            "anc_days": anc,
            "amount": total,
            "soname": soname,
        })

    print("\n[*] ALERTES — visites < 14 jours après dernière SO (trop rapprochées) :")
    found_alert = False
    for r in results:
        if r["anc_days"] != "-" and r["anc_days"] != "Jamais":
            j = int(r["anc_days"].rstrip("j"))
            if j < 14:
                print(f"    ⚠ {r['day']} {r['label']} — dernière SO {r['last_so_date']} ({r['anc_days']}) — visite trop rapprochée ?")
                found_alert = True
    if not found_alert:
        print("    (aucune)")


if __name__ == "__main__":
    main()
