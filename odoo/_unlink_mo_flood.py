"""Unlink des 194 MO flood 2026-04-21 (state=cancel)."""
import xmlrpc.client
import json
from datetime import datetime

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

report = {"ts": datetime.now().isoformat(), "steps": []}

# Step 1 : recompte exact - MO cancel créés >= 2026-04-21 12:00
domain = [
    ("state", "=", "cancel"),
    ("create_date", ">=", "2026-04-21 12:00:00"),
]
ids = call("mrp.production", "search", [domain])
count = len(ids)
report["steps"].append({"step": "count_cancel_flood", "count": count, "ids": ids})
print(f"[1] MO cancel flood count: {count}")

if count != 194:
    print(f"ABORT : count {count} != 194")
    report["aborted"] = f"count mismatch {count}"
    with open("odoo/_unlink_mo_flood_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    raise SystemExit(1)

# Step 2 : vérif move_raw_ids done
raw_done = call("stock.move", "search_count", [[
    ("raw_material_production_id", "in", ids),
    ("state", "=", "done"),
]])
report["steps"].append({"step": "raw_done_count", "count": raw_done})
print(f"[2] Raw moves done: {raw_done}")

# Step 3 : vérif move_finished_ids done
fin_done = call("stock.move", "search_count", [[
    ("production_id", "in", ids),
    ("state", "=", "done"),
]])
report["steps"].append({"step": "finished_done_count", "count": fin_done})
print(f"[3] Finished moves done: {fin_done}")

if raw_done > 0 or fin_done > 0:
    print(f"ABORT : done moves trouvés raw={raw_done} fin={fin_done}")
    report["aborted"] = "done moves exist"
    with open("odoo/_unlink_mo_flood_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    raise SystemExit(1)

# Step 4 : warning procurement_group_id → SO active
mos_data = call("mrp.production", "read", [ids, ["id", "name", "procurement_group_id", "origin"]])
so_linked = []
for mo in mos_data:
    if mo.get("procurement_group_id"):
        pg_id = mo["procurement_group_id"][0]
        so = call("sale.order", "search", [[("procurement_group_id", "=", pg_id), ("state", "not in", ["cancel", "draft"])]])
        if so:
            so_linked.append({"mo_id": mo["id"], "mo_name": mo["name"], "so_ids": so})
report["steps"].append({"step": "so_linked_warnings", "count": len(so_linked), "items": so_linked})
print(f"[4] MO liés à SO actives: {len(so_linked)} (warning seulement, on continue)")

# Step 5 : unlink par batch de 50
print(f"[5] Unlink {count} MO par batch de 50...")
unlinked = 0
errors = []
for i in range(0, count, 50):
    batch = ids[i:i+50]
    try:
        call("mrp.production", "unlink", [batch])
        unlinked += len(batch)
        print(f"   batch {i//50 + 1}: {len(batch)} OK (total {unlinked})")
    except Exception as e:
        errors.append({"batch_start": i, "error": str(e), "ids": batch})
        print(f"   batch {i//50 + 1}: ERROR {e}")

report["steps"].append({"step": "unlink", "unlinked": unlinked, "errors": errors})

# Step 6 : recompte
remain_cancel = call("mrp.production", "search_count", [domain])
remain_all = call("mrp.production", "search_count", [[("create_date", ">=", "2026-04-21 12:00:00")]])
report["steps"].append({
    "step": "post_verify",
    "remaining_cancel_flood": remain_cancel,
    "remaining_all_today_after_noon": remain_all,
})
print(f"[6] Remaining cancel flood: {remain_cancel} | Remaining total >= 12:00: {remain_all}")

with open("odoo/_unlink_mo_flood_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, default=str)

print("DONE")
