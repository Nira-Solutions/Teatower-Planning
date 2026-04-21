"""
Annulation SAFE du flood de MO généré par le cron scheduler 2026-04-21 14:29
suite à la réactivation de la route Manufacture (commit d67ef22 à ~14:2x).

REGLE : on n'annule QUE les MO en state draft/confirmed créés APRES 12:00 aujourd'hui.
On ne touche PAS à progress/to_close/done.

Usage :
  python _cancel_mo_flood.py             # DRY-RUN (liste ce qui serait annulé)
  python _cancel_mo_flood.py --execute   # annule réellement
"""
import xmlrpc.client, sys, json
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

EXECUTE = "--execute" in sys.argv
CUTOFF = "2026-04-21 12:00:00"

# 1. Sélection stricte : état annulable + créés aujourd'hui
target = call("mrp.production","search",[[
    ("create_date",">=",CUTOFF),
    ("state","in",["draft","confirmed"]),
]], {"order":"id asc"})

print(f"MO candidats (state in draft/confirmed, create_date >= {CUTOFF}) : {len(target)}")

# 2. Vérif double : aucun raw move déjà consommé
if target:
    bad_moves = call("stock.move","search_count",[[
        ("raw_material_production_id","in",target),
        ("state","=","done"),
    ]])
    print(f"Raw moves déjà DONE sur ces MO : {bad_moves} (doit être 0)")
    if bad_moves:
        print("ABORT — du stock a déjà été consommé sur au moins 1 MO. Inspection manuelle requise.")
        sys.exit(2)

if not EXECUTE:
    print("DRY-RUN — relancer avec --execute pour annuler.")
    # Dump liste pour trace
    sample = call("mrp.production","read",[target[:20],["name","product_id","product_qty","state"]])
    for r in sample:
        print(f"  {r['name']} | {r['product_id'][1]} | qty={r['product_qty']} | {r['state']}")
    sys.exit(0)

# 3. Exécution par chunks de 100
ok, fail = 0, []
for i in range(0, len(target), 100):
    chunk = target[i:i+100]
    try:
        call("mrp.production","action_cancel",[chunk])
        ok += len(chunk)
        print(f"  action_cancel OK : {i+len(chunk)}/{len(target)}")
    except Exception as e:
        print(f"  FAIL chunk {i}: {e}")
        # Fallback record par record
        for rid in chunk:
            try:
                call("mrp.production","action_cancel",[[rid]])
                ok += 1
            except Exception as e2:
                fail.append((rid, str(e2)[:120]))

print(f"\nRésultat : {ok} annulés, {len(fail)} échecs.")
if fail:
    with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/_mo_cancel_failures.json","w",encoding="utf-8") as f:
        json.dump(fail, f, indent=2)
    print("Détails : odoo/_mo_cancel_failures.json")
