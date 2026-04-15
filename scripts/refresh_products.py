"""Regenerate data/products.json (SKU + name only, no price) from Odoo cache.

Usage:
    python scripts/refresh_products.py

Reads data/odoo_products_all.json (maintained by other pipelines) and writes
data/products.json — a slim file served by GitHub Pages to feed the SKU
autocomplete in commande.html.

No prices exposed: B2B tariffs vary per customer, and the operator types the
right price manually in the web form.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "odoo_products_all.json"
DST = ROOT / "data" / "products.json"


def main() -> None:
    products = json.loads(SRC.read_text(encoding="utf-8"))

    slim = []
    for p in products:
        if not p.get("active") or not p.get("sale_ok"):
            continue
        code = p.get("default_code")
        name = p.get("name")
        if not code or not name:
            continue
        slim.append({"sku": code, "name": name})

    slim.sort(key=lambda r: r["sku"])

    DST.write_text(
        json.dumps(slim, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"wrote {DST} — {len(slim)} products")


if __name__ == "__main__":
    main()
