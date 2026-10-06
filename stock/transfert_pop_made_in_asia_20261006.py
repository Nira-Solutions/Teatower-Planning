# -*- coding: utf-8 -*-
"""
Transfert TT/Stock -> POP/Stock pour le salon Made in Asia — 06/10/2026.

Schéma maison (cf. transfert_magasins_20260909.py) : type « Transferts internes »
du magasin destinataire (68 = POP-UP STORE), source TT/Stock, confirmé et
réservé, PAS validé.

Résolutions de codes : « 1152 » -> A1152, « a304 » -> A0304,
EM0106 -> product 7770 (le 7707 est archivé).

    python transfert_pop_made_in_asia_20261006.py         -> DRY-RUN
    python transfert_pop_made_in_asia_20261006.py apply   -> exécution
"""
import os
import sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
PWD = os.environ["ODOO_PWD"]
UID = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, "nicolas.raes@teatower.com", PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return _m.execute_kw(DB, UID, PWD, model, method, args, kw or {})


APPLY = "apply" in [a.lower() for a in sys.argv[1:]]
SRC, DEST, PTYPE = 8, 4575, 68          # TT/Stock -> POP/Stock
ORIGINE = "Salon Made in Asia 2026"
LIGNES = [  # (product_id, code, qté)
    (5221, "V0895", 35), (7054, "V0910", 30), (5230, "V0907", 30), (7733, "C0200", 20),
    (4046, "A0297", 30), (4047, "A0298", 30), (4056, "A0511", 20), (4203, "A1074", 15),
    (4204, "A1075", 20), (4209, "A1080", 20), (7481, "A1133", 20), (7482, "A1134", 30),
    (7483, "A1135", 20), (7493, "MIA26", 150), (5104, "V0711", 80), (5115, "V0732", 80),
    (5217, "V0891", 80), (7663, "V0917", 80), (7664, "V0918", 80), (7658, "C0195", 45),
    (7660, "C0197", 60), (7659, "C0196", 60), (4044, "A0271", 30), (4042, "A0261", 30),
    (7661, "C0198", 16), (4261, "C0102", 25), (7770, "EM0106", 1), (7876, "A1149", 12),
    (7878, "A1151", 24), (7879, "A1152", 12), (7880, "A1153", 12), (7881, "A1154", 24),
    (7882, "A1155", 25), (7897, "A1158", 25), (4049, "A0304", 30), (4253, "C0023", 400),
    (7240, "D011", 500),
]

info = {p["id"]: p for p in call("product.product", "read", [[l[0] for l in LIGNES]],
                                  {"fields": ["free_qty", "incoming_qty"]})}
print(f"=== {len(LIGNES)} lignes TT/Stock -> POP/Stock ===")
for pid, code, q in LIGNES:
    f = info[pid]["free_qty"]
    flag = "" if f >= q else f"  <-- libre {f:g}, entrant {info[pid]['incoming_qty']:g}"
    print(f"  {q:>4} x {code}{flag}")
if not APPLY:
    print("\nDRY-RUN — relancer avec 'apply'.")
    sys.exit(0)

pk = call("stock.picking", "create", [{
    "picking_type_id": PTYPE, "location_id": SRC, "location_dest_id": DEST, "origin": ORIGINE,
    "move_ids_without_package": [(0, 0, {"name": code, "product_id": pid, "product_uom_qty": q,
                                         "location_id": SRC, "location_dest_id": DEST})
                                 for pid, code, q in LIGNES],
}])
for meth in ("action_confirm", "action_assign"):
    try:
        call("stock.picking", meth, [[pk]])
    except xmlrpc.client.Fault as e:
        if "cannot marshal None" not in str(e):
            raise
p = call("stock.picking", "read", [[pk]], {"fields": ["name", "state", "move_ids"]})[0]
print(f"\n-> {p['name']} (id {pk}) état {p['state']}")
for mv in call("stock.move", "read", [p["move_ids"]], {"fields": ["product_id", "product_uom_qty", "quantity", "state"]}):
    if mv["quantity"] < mv["product_uom_qty"]:
        print(f"   non réservé : {mv['product_id'][1][:50]}  {mv['quantity']:g}/{mv['product_uom_qty']:g}")
