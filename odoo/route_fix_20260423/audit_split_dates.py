"""Split rows by write_date to isolate the 2026-04-23 batch."""
import json, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
data = json.load(open("C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423/audit_i0v0_buy.json", encoding="utf-8"))
rows = data["rows"]

with_bom = [r for r in rows if r["n_bom_active"] > 0]
print(f"Total I0/V0 Buy + BoM active : {len(with_bom)}")
# Bucket by date
buckets = Counter()
for r in with_bom:
    wd = (r.get("write_date") or "")[:10]
    buckets[wd] += 1
print("\nWrite_date buckets (BoM active) :")
for d, n in sorted(buckets.items(), reverse=True)[:20]:
    print(f"  {d} : {n}")

# Cross-ref with 11_restore_report.json (the 256 OP IDs touched by the script)
import json as j
report = j.load(open("C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423/11_restore_report.json", encoding="utf-8"))
# That report stores no_vendor_rows + mo_confirmed_rows but NOT the 256 ids of with_vendor.
# Use write_date == 2026-04-23 as a proxy
on_2304 = [r for r in with_bom if (r.get("write_date") or "").startswith("2026-04-23")]
print(f"\nI0/V0 Buy + BoM active modifies le 2026-04-23 : {len(on_2304)}")

# Detail
i0_2304 = [r for r in on_2304 if r["fam"] == "I0"]
v0_2304 = [r for r in on_2304 if r["fam"] == "V0"]
print(f"  I0 : {len(i0_2304)}")
print(f"  V0 : {len(v0_2304)}")

# All-time problematic (regardless of date) - these are the ones to fix
print("\n=== A CORRIGER (route Buy + BoM active, toutes dates) ===")
print(f"  Total : {len(with_bom)}")
print(f"  I0    : {sum(1 for r in with_bom if r['fam']=='I0')}")
print(f"  V0    : {sum(1 for r in with_bom if r['fam']=='V0')}")

# Save short list
out_rows = sorted(with_bom, key=lambda r: r["code"] or "")
import os
with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423/i0v0_buy_with_bom_TO_FIX.json",
          "w", encoding="utf-8") as f:
    json.dump({"n": len(out_rows), "rows": out_rows}, f, indent=2, default=str, ensure_ascii=False)
print("\nfichier : i0v0_buy_with_bom_TO_FIX.json")

# Markdown table
lines = ["# OP I0/V0 sur route Buy avec BoM active (a corriger -> Manufacture)",
         "",
         f"Genere : 2026-04-27 / Total : **{len(out_rows)}**",
         "",
         f"- I0 (infusions) : {sum(1 for r in out_rows if r['fam']=='I0')}",
         f"- V0 (vrac)      : {sum(1 for r in out_rows if r['fam']=='V0')}",
         "",
         "| Code | Famille | Nom | OP | Min | Max | Route actuelle | Write date | n BoM |",
         "|---|---|---|---|---|---|---|---|---|"]
for r in out_rows:
    lines.append(
        f"| {r['code']} | {r['fam']} | {r['name'][:60]} | {r['op_name']} | {r['min']} | {r['max']} | {r['route']} | {(r.get('write_date') or '')[:10]} | {r['n_bom_active']} |"
    )
with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423/i0v0_buy_with_bom_TO_FIX.md",
          "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("fichier : i0v0_buy_with_bom_TO_FIX.md")
