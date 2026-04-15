"""Process pending orders dropped in inbox/ by the web form.

Reads every inbox/<order_id>/order.json, creates a draft sale.order in Odoo
via XML-RPC, then moves the whole folder to archive/ so it is preserved.

On errors (unknown client, ambiguous match, missing SKU) the order stays in
inbox/ with an error marker file next to it — a human reviews and fixes.

Secrets (GitHub Actions env):
    ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PWD
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import xmlrpc.client
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "inbox"
ARCHIVE = ROOT / "archive"

ODOO_URL = os.environ["ODOO_URL"]
ODOO_DB = os.environ["ODOO_DB"]
ODOO_USER = os.environ["ODOO_USER"]
ODOO_PWD = os.environ["ODOO_PWD"]


class Odoo:
    def __init__(self) -> None:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        self.uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
        if not self.uid:
            raise RuntimeError("Odoo authentication failed")
        self.models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

    def call(self, model: str, method: str, args: list, kwargs: dict | None = None) -> Any:
        return self.models.execute_kw(ODOO_DB, self.uid, ODOO_PWD, model, method, args, kwargs or {})


def find_partner(odoo: Odoo, name: str) -> tuple[int | None, str]:
    """Return (partner_id, status). status in {ok, not_found, ambiguous}."""
    name = name.strip()
    # Exact match first
    exact = odoo.call("res.partner", "search", [[("name", "=", name), ("customer_rank", ">", 0)]], {"limit": 5})
    if len(exact) == 1:
        return exact[0], "ok"
    # Fuzzy ilike
    hits = odoo.call("res.partner", "search", [[("name", "ilike", name), ("customer_rank", ">", 0)]], {"limit": 10})
    if not hits:
        # Widen: any partner
        hits = odoo.call("res.partner", "search", [[("name", "ilike", name)]], {"limit": 10})
    if not hits:
        return None, "not_found"
    if len(hits) == 1:
        return hits[0], "ok"
    # Multiple: prefer exact case-insensitive
    for pid in hits:
        p = odoo.call("res.partner", "read", [[pid]], {"fields": ["name"]})[0]
        if p["name"].strip().lower() == name.lower():
            return pid, "ok"
    return None, "ambiguous"


def find_products(odoo: Odoo, skus: list[str]) -> tuple[dict[str, int], list[str]]:
    found: dict[str, int] = {}
    missing: list[str] = []
    for sku in skus:
        pids = odoo.call("product.product", "search", [[("default_code", "=", sku)]], {"limit": 1})
        if pids:
            found[sku] = pids[0]
        else:
            missing.append(sku)
    return found, missing


def process_one(order_dir: Path, odoo: Odoo) -> tuple[bool, str]:
    order_json = order_dir / "order.json"
    if not order_json.exists():
        return False, "order.json missing"

    data = json.loads(order_json.read_text(encoding="utf-8"))

    partner_id, p_status = find_partner(odoo, data["client_name"])
    if p_status != "ok":
        return False, f"client '{data['client_name']}' → {p_status}"

    skus = [l["sku"] for l in data["lines"]]
    products, missing = find_products(odoo, skus)
    if missing:
        return False, f"unknown SKU(s): {', '.join(missing)}"

    order_lines = []
    for l in data["lines"]:
        order_lines.append((0, 0, {
            "product_id": products[l["sku"]],
            "product_uom_qty": l["qty"],
            "price_unit": l["price"],
            "discount": l.get("discount") or 0.0,
        }))

    vals: dict[str, Any] = {
        "partner_id": partner_id,
        "order_line": order_lines,
    }
    if data.get("client_ref"):
        vals["client_order_ref"] = data["client_ref"]
    if data.get("delivery_date"):
        vals["commitment_date"] = data["delivery_date"] + " 00:00:00"
    if data.get("notes"):
        vals["note"] = data["notes"]

    so_id = odoo.call("sale.order", "create", [vals])
    so = odoo.call("sale.order", "read", [[so_id]], {"fields": ["name", "amount_total"]})[0]

    result = {
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "odoo_sale_order_id": so_id,
        "odoo_sale_order_name": so["name"],
        "amount_total": so["amount_total"],
        "partner_id": partner_id,
        "contact_email": data.get("contact_email"),
    }
    (order_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return True, f"{so['name']} ({so['amount_total']:.2f}€)"


def main() -> int:
    if not INBOX.exists():
        print("no inbox/")
        return 0
    pending = sorted([d for d in INBOX.iterdir() if d.is_dir()])
    if not pending:
        print("inbox empty")
        return 0

    ARCHIVE.mkdir(exist_ok=True)
    odoo = Odoo()

    n_ok = n_err = 0
    for order_dir in pending:
        try:
            ok, msg = process_one(order_dir, odoo)
        except Exception as e:
            ok, msg = False, f"exception: {e}"

        if ok:
            n_ok += 1
            dest = ARCHIVE / order_dir.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.move(str(order_dir), str(dest))
            print(f"OK  {order_dir.name}: {msg}")
        else:
            n_err += 1
            err_marker = order_dir / "ERROR.txt"
            err_marker.write_text(
                f"{datetime.utcnow().isoformat()}Z\n{msg}\n",
                encoding="utf-8",
            )
            print(f"ERR {order_dir.name}: {msg}")

    print(f"\ntotal: {n_ok} ok, {n_err} errors")
    return 0 if n_err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
