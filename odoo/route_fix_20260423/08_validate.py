"""
Validation post-fix : declencher un mini scheduler run sur un OP test
et verifier que ca produit bien un PO (pas un MO).

Plutot que de declencher tout le scheduler (lourd), on pose sur un OP test.
Ou on regarde simplement les stock.rule operantes pour les produits concernes.
"""
import xmlrpc.client, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

# Check : pour chaque warehouse, quelles routes sont actives avec rules actives ?
print("=== Routes actives + rules operantes par warehouse ===", flush=True)

for wh_id in [1, 2, 3, 4, 5, 6, 7, 8]:
    wh = call("stock.warehouse", "read", [[wh_id], ["name", "code", "route_ids", "buy_to_resupply", "manufacture_to_resupply"]])[0]
    print(f"\n  {wh['code']} ({wh['name']}) : route_ids={wh['route_ids']} | buy={wh['buy_to_resupply']} mfg={wh['manufacture_to_resupply']}", flush=True)

# Check routes 5 (Buy) et 6 (Manufacture) : rules avec destination ?
print("\n=== Rules Buy (route 5) actives ===", flush=True)
r5 = call("stock.rule", "search_read",
          [[("route_id", "=", 5), ("active", "=", True)]],
          {"fields": ["id", "name", "action", "location_dest_id", "picking_type_id"]})
for r in r5:
    print(f"  id={r['id']} | {r['name']} | action={r['action']} | dest={r['location_dest_id']} | picking_type={r['picking_type_id']}", flush=True)

print("\n=== Rules Manufacture (route 6) actives ===", flush=True)
r6 = call("stock.rule", "search_read",
          [[("route_id", "=", 6), ("active", "=", True)]],
          {"fields": ["id", "name", "action", "location_dest_id", "picking_type_id"]})
for r in r6:
    print(f"  id={r['id']} | {r['name']} | action={r['action']} | dest={r['location_dest_id']}", flush=True)

# Test : run scheduler sur 1 OP test ?
# Trop risque de relancer le flood. On verifie just le plan theorique.

# Check 1 produit fournisseur : quelle route sera prise ?
# Pour TT/Stock (location_id=8), on cherche les rules actives qui peuvent l'alimenter.
print("\n=== Rules qui alimentent TT/Stock (loc 8) avec action=buy ou manufacture ===", flush=True)
rules_tt = call("stock.rule", "search_read",
                [[("location_dest_id", "=", 8), ("active", "=", True), ("action", "in", ["buy", "manufacture"])]],
                {"fields": ["id", "name", "action", "route_id", "sequence"]})
for r in rules_tt:
    print(f"  id={r['id']} | {r['name']} | action={r['action']} | route={r['route_id']} | seq={r['sequence']}", flush=True)

# Relancer le scheduler pour qu'il regenere les procurements corrects ?
# Ca genere des PO pour les OP vraiment sous le min. Nicolas veut qu'il relance ca.
print("\n=== Relancer procurement scheduler ? ===", flush=True)
# On l'offre mais en mode suggestion, pas automatique
print("Pour relancer : call('procurement.group', 'run_scheduler', [])", flush=True)
