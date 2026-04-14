"""
Shopify -> Odoo photos sync for products flagged 'manual' in
output/product_photos_plan.json.

Pipeline:
 1. Scrape https://teatower.com/products.json (paginate).
 2. Match variant.sku <-> default_code (exact), fallback fuzzy on name.
 3. Download images[0].src, upload to product.template.image_1920.
 4. Batch 50 writes, log to output/product_photos_shopify_log.json.
"""
import base64
import json
import os
import sys
import time
import difflib
import urllib.request
import urllib.error
import xmlrpc.client
from pathlib import Path

ROOT = Path(r"C:/Users/FlowUP/Downloads/Claude/Claude/Teatower")
PLAN = ROOT / "output" / "product_photos_refresh_log.json"
LOG = ROOT / "output" / "product_photos_shopify_log.json"
SHOPIFY_BASE = "https://teatower.com/products.json"

ODOO_URL = "https://tea-tree.odoo.com"
ODOO_DB = "tsc-be-tea-tree-main-18515272"
ODOO_USER = "nicolas.raes@teatower.com"
ODOO_PWD = os.environ.get("ODOO_API_KEY") or os.environ.get("ODOO_PWD")


def http_get(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TeatowerBot/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10)
                continue
            raise
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(3)


def scrape_shopify():
    all_products = []
    page = 1
    while True:
        url = f"{SHOPIFY_BASE}?limit=250&page={page}"
        print(f"[shopify] page {page}", flush=True)
        raw = http_get(url)
        data = json.loads(raw)
        prods = data.get("products", [])
        if not prods:
            break
        all_products.extend(prods)
        if len(prods) < 250:
            break
        page += 1
        time.sleep(0.5)
    return all_products


def norm(s):
    return "".join(c.lower() for c in (s or "") if c.isalnum() or c.isspace()).strip()


def main():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    # plan structure fallback
    if isinstance(plan, dict):
        items = plan.get("manual") or plan.get("products") or plan.get("items") or []
    else:
        items = plan
    for it in items:
        it.setdefault("default_code", it.get("ref"))
    print(f"[plan] {len(items)} produits manual a traiter", flush=True)

    shopify = scrape_shopify()
    print(f"[shopify] {len(shopify)} produits scrapes", flush=True)

    # Build SKU -> (product, image)
    sku_idx = {}
    title_idx = {}
    for sp in shopify:
        img = (sp.get("images") or [{}])[0].get("src") if sp.get("images") else None
        if not img:
            continue
        title_idx[norm(sp.get("title"))] = (sp, img)
        for v in sp.get("variants", []):
            sku = (v.get("sku") or "").strip()
            if sku:
                sku_idx[sku] = (sp, img)

    log = []
    matches = []

    for it in items:
        code = (it.get("default_code") or "").strip()
        name = it.get("name") or ""
        tid = it.get("id")

        hit = sku_idx.get(code) if code else None
        match_type = "sku" if hit else None

        if not hit and code:
            # try with I0 normalized
            alt = code.replace("IO", "I0") if code.startswith("IO") else code
            hit = sku_idx.get(alt)
            if hit:
                match_type = "sku_norm"

        if not hit and name:
            # fuzzy
            best = difflib.get_close_matches(norm(name), list(title_idx.keys()), n=1, cutoff=0.75)
            if best:
                hit = title_idx[best[0]]
                match_type = f"fuzzy:{best[0][:40]}"

        if not hit:
            log.append({"ref": code, "name": name, "id": tid, "status": "no_match"})
            continue

        sp, img_url = hit
        matches.append({"id": tid, "ref": code, "name": name,
                        "shopify_id": sp.get("id"), "image_url": img_url,
                        "match": match_type})

    print(f"[match] total={len(matches)} no_match={sum(1 for l in log if l['status']=='no_match')}", flush=True)

    # Odoo login
    if not ODOO_PWD:
        print("[odoo] ERROR: no ODOO_API_KEY / ODOO_PWD env var", flush=True)
        LOG.write_text(json.dumps({"matches": matches, "log": log}, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    print(f"[odoo] uid={uid}", flush=True)

    # Batch 50
    done = failed = 0
    for i in range(0, len(matches), 50):
        batch = matches[i:i+50]
        for m in batch:
            try:
                img_bytes = http_get(m["image_url"])
                b64 = base64.b64encode(img_bytes).decode()
                models.execute_kw(ODOO_DB, uid, ODOO_PWD, "product.template",
                                  "write", [[m["id"]], {"image_1920": b64}])
                log.append({"ref": m["ref"], "name": m["name"],
                            "shopify_product_id": m["shopify_id"],
                            "image_url": m["image_url"],
                            "match": m["match"], "status": "done"})
                done += 1
            except Exception as e:
                log.append({"ref": m["ref"], "name": m["name"],
                            "shopify_product_id": m["shopify_id"],
                            "image_url": m["image_url"],
                            "match": m["match"], "status": "failed",
                            "error": str(e)[:200]})
                failed += 1
        print(f"[odoo] batch {i//50+1}: done={done} failed={failed}", flush=True)
        time.sleep(0.3)

    LOG.write_text(json.dumps({
        "summary": {
            "shopify_total": len(shopify),
            "plan_total": len(items),
            "matches_total": len(matches),
            "sku_exact": sum(1 for m in matches if m["match"] == "sku"),
            "sku_norm": sum(1 for m in matches if m["match"] == "sku_norm"),
            "fuzzy": sum(1 for m in matches if m["match"].startswith("fuzzy")),
            "odoo_done": done,
            "odoo_failed": failed,
            "no_match": sum(1 for l in log if l["status"] == "no_match"),
        },
        "log": log
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[log] ecrit {LOG}", flush=True)


if __name__ == "__main__":
    main()
