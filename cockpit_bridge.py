"""
Cockpit Bridge — relais local entre teatower_cockpit.html et les agents Claude Code.

Lance : python cockpit_bridge.py
        (puis ouvre teatower_cockpit.html dans le navigateur)

Endpoints :
  POST /run        body {action, prompt}   → lance 'claude -p "<prompt>"', retourne task_id
  GET  /tasks                              → liste de toutes les tâches
  GET  /tasks/{id}                         → détail + logs tail
  POST /tasks/{id}/stop                    → kill la tâche
"""
from __future__ import annotations

import os
import shutil
import subprocess
import threading
import time
import uuid
import xmlrpc.client
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import request as urlreq, error as urlerr
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ODOO_URL = os.getenv("ODOO_URL", "https://tea-tree.odoo.com")
ODOO_DB = os.getenv("ODOO_DB", "tsc-be-tea-tree-main-18515272")
ODOO_USER = os.getenv("ODOO_USER", "nicolas.raes@teatower.com")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "Teatower123")

SHOPIFY_SHOP = os.getenv("SHOPIFY_SHOP", "")
SHOPIFY_TOKEN = os.getenv("SHOPIFY_TOKEN", "")

GMS_KEYWORDS = ("delhaize", "carrefour", "ad ", "spar", "cora", "match", "intermarche",
                "auchan", "colruyt", "okay", "proxy", "lidl", "aldi", "louis delhaize")

_odoo_cache: dict[str, tuple[float, Any]] = {}
CACHE_TTL = 60

ROOT = Path(__file__).parent.resolve()
LOG_DIR = ROOT / ".claude" / "cockpit_tasks"
LOG_DIR.mkdir(parents=True, exist_ok=True)

CLAUDE_BIN = shutil.which("claude") or "claude"

app = FastAPI(title="Teatower Cockpit Bridge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TASKS: dict[str, dict] = {}
_lock = threading.Lock()


class RunRequest(BaseModel):
    action: str
    prompt: str


def _run_claude(task_id: str, prompt: str) -> None:
    t = TASKS[task_id]
    log_path = LOG_DIR / f"{task_id}.log"
    t["log_path"] = str(log_path)
    t["status"] = "running"
    t["started_at"] = time.time()

    cmd = [CLAUDE_BIN, "-p", prompt, "--permission-mode", "bypassPermissions"]
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"$ {' '.join(cmd)}\n\n")
            f.flush()
            proc = subprocess.Popen(
                cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                cwd=str(ROOT),
                shell=False,
            )
            t["pid"] = proc.pid
            rc = proc.wait()
        t["return_code"] = rc
        t["status"] = "done" if rc == 0 else "failed"
    except Exception as e:
        t["status"] = "error"
        t["error"] = str(e)
    finally:
        t["ended_at"] = time.time()


@app.post("/run")
def run(req: RunRequest):
    task_id = uuid.uuid4().hex[:8]
    with _lock:
        TASKS[task_id] = {
            "id": task_id,
            "action": req.action,
            "prompt": req.prompt,
            "status": "queued",
            "created_at": time.time(),
        }
    threading.Thread(target=_run_claude, args=(task_id, req.prompt), daemon=True).start()
    return {"task_id": task_id}


@app.get("/tasks")
def list_tasks():
    return sorted(TASKS.values(), key=lambda t: t.get("created_at", 0), reverse=True)


@app.get("/tasks/{task_id}")
def get_task(task_id: str, tail: int = 80):
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(404, "task not found")
    log_lines: list[str] = []
    lp = t.get("log_path")
    if lp and os.path.exists(lp):
        with open(lp, "r", encoding="utf-8", errors="replace") as f:
            log_lines = f.readlines()[-tail:]
    return {**t, "log_tail": "".join(log_lines)}


@app.post("/tasks/{task_id}/stop")
def stop_task(task_id: str):
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(404, "task not found")
    pid = t.get("pid")
    if pid and t.get("status") == "running":
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
            else:
                os.kill(pid, 15)
            t["status"] = "stopped"
        except Exception as e:
            raise HTTPException(500, str(e))
    return {"ok": True, "status": t.get("status")}


@app.get("/")
def health():
    return {"ok": True, "claude": CLAUDE_BIN, "cwd": str(ROOT), "tasks": len(TASKS)}


# ============================================================
#                  ODOO LIVE DATA
# ============================================================

def _odoo_call(model: str, method: str, args: list, kw: dict | None = None):
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        raise RuntimeError("Odoo auth failed")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model, method, args, kw or {})


def _cached(key: str, fn, ttl: int = CACHE_TTL):
    now = time.time()
    if key in _odoo_cache:
        ts, val = _odoo_cache[key]
        if now - ts < ttl:
            return val
    val = fn()
    _odoo_cache[key] = (now, val)
    return val


def _classify_partner(name: str) -> str:
    n = (name or "").lower()
    for kw in GMS_KEYWORDS:
        if kw in n:
            return "GMS"
    if any(x in n for x in ("hotel", "radisson", "marriott", "sofitel", "ibis")):
        return "Hotellerie"
    if any(x in n for x in ("restaurant", "brasserie", "café", "cafe", "bistrot")):
        return "Horeca"
    if any(x in n for x in ("hopital", "hôpital", "clinique", "ehpad", "maison de repos")):
        return "Institution"
    return "Autres B2B"


@app.get("/odoo/health")
def odoo_health():
    try:
        uid = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common").authenticate(
            ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        return {"ok": bool(uid), "uid": uid, "url": ODOO_URL, "db": ODOO_DB}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/odoo/boutiques")
def odoo_boutiques():
    """CA + tickets par warehouse boutique sur les 7 derniers jours."""
    def _fetch():
        since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
        warehouses = _odoo_call("stock.warehouse", "search_read",
                                [[]], {"fields": ["id", "name", "code"]})
        wh_map = {w["id"]: w for w in warehouses}
        orders = _odoo_call("sale.order", "search_read",
                            [[("date_order", ">=", since), ("state", "in", ["sale", "done"])]],
                            {"fields": ["id", "warehouse_id", "amount_total", "partner_id"], "limit": 5000})
        agg = defaultdict(lambda: {"ca": 0.0, "tickets": 0})
        for o in orders:
            wid = (o.get("warehouse_id") or [0])[0]
            agg[wid]["ca"] += o.get("amount_total", 0)
            agg[wid]["tickets"] += 1

        boutiques = []
        wanted = ("waterloo", "liège", "liege", "namur", "wat", "lge", "nam")
        for wid, w in wh_map.items():
            n = (w["name"] or "").lower()
            if any(k in n for k in wanted):
                a = agg.get(wid, {"ca": 0.0, "tickets": 0})
                boutiques.append({
                    "id": w.get("code") or str(wid),
                    "name": f"Teatower {w['name']}",
                    "city": w["name"],
                    "ca7": round(a["ca"], 2),
                    "tickets": a["tickets"],
                    "basket": round(a["ca"] / a["tickets"], 2) if a["tickets"] else 0,
                })
        return {"_live": True, "since": since, "boutiques": boutiques}

    try:
        return _cached("boutiques", _fetch)
    except Exception as e:
        return {"_live": False, "error": str(e)}


@app.get("/odoo/b2b")
def odoo_b2b():
    """CA B2B 30j split GMS / Horeca / Autres."""
    def _fetch():
        since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d 00:00:00")
        orders = _odoo_call("sale.order", "search_read",
                            [[("date_order", ">=", since), ("state", "in", ["sale", "done"])]],
                            {"fields": ["partner_id", "amount_total", "date_order"], "limit": 5000})
        per_partner = defaultdict(lambda: {"ca": 0.0, "n": 0})
        for o in orders:
            pid = (o.get("partner_id") or [0, "Inconnu"])
            per_partner[pid[1]]["ca"] += o.get("amount_total", 0)
            per_partner[pid[1]]["n"] += 1

        gms_groups = defaultdict(lambda: {"ca": 0.0, "stores": 0})
        others = []
        for name, v in per_partner.items():
            cat = _classify_partner(name)
            if cat == "GMS":
                # group enseigne
                low = name.lower()
                key = next((k.title().strip() for k in GMS_KEYWORDS if k in low), name)
                gms_groups[key]["ca"] += v["ca"]
                gms_groups[key]["stores"] += 1
            else:
                others.append({"name": name, "type": cat, "ca30": round(v["ca"], 2)})

        gms = [{"name": k, "ca30": round(v["ca"], 2), "stores": v["stores"]}
               for k, v in gms_groups.items()]
        gms.sort(key=lambda x: -x["ca30"])
        others.sort(key=lambda x: -x["ca30"])
        return {"_live": True, "since": since, "gms": gms, "others": others[:30]}

    try:
        return _cached("b2b", _fetch)
    except Exception as e:
        return {"_live": False, "error": str(e)}


@app.get("/odoo/b2b-orders")
def odoo_b2b_orders():
    """Commandes B2B en cours (draft/sent/sale)."""
    def _fetch():
        orders = _odoo_call("sale.order", "search_read",
                            [[("state", "in", ["draft", "sent", "sale"])]],
                            {"fields": ["name", "partner_id", "amount_total", "date_order", "state"],
                             "limit": 30, "order": "date_order desc"})
        out = []
        for o in orders:
            pname = (o.get("partner_id") or [0, "?"])[1]
            out.append({
                "name": o["name"],
                "client": pname,
                "canal": _classify_partner(pname),
                "date": (o.get("date_order") or "")[:10],
                "amount": round(o.get("amount_total", 0), 2),
                "status": o["state"],
            })
        return {"_live": True, "orders": out}

    try:
        return _cached("b2b_orders", _fetch)
    except Exception as e:
        return {"_live": False, "error": str(e)}


# ============================================================
#                  SHOPIFY LIVE DATA
# ============================================================

@app.get("/shopify/orders")
def shopify_orders(days: int = 7):
    if not (SHOPIFY_SHOP and SHOPIFY_TOKEN):
        return {"_live": False, "error": "SHOPIFY_SHOP / SHOPIFY_TOKEN env vars not set"}

    def _fetch():
        since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = (f"https://{SHOPIFY_SHOP}/admin/api/2024-10/orders.json"
               f"?status=any&created_at_min={since}&limit=250")
        req = urlreq.Request(url, headers={
            "X-Shopify-Access-Token": SHOPIFY_TOKEN,
            "Content-Type": "application/json",
        })
        with urlreq.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        orders = data.get("orders", [])
        ca = sum(float(o.get("total_price", 0)) for o in orders)
        countries = defaultdict(lambda: {"ca": 0.0, "n": 0})
        products = defaultdict(lambda: {"qty": 0, "ca": 0.0})
        to_ship = 0
        recent = []
        for o in orders:
            cc = (o.get("shipping_address") or {}).get("country_code", "??")
            countries[cc]["ca"] += float(o.get("total_price", 0))
            countries[cc]["n"] += 1
            if o.get("fulfillment_status") in (None, "partial"):
                to_ship += 1
            for li in o.get("line_items", []):
                products[li["title"]]["qty"] += li.get("quantity", 0)
                products[li["title"]]["ca"] += float(li.get("price", 0)) * li.get("quantity", 0)
            if len(recent) < 10:
                recent.append({
                    "n": o.get("name"),
                    "client": ((o.get("customer") or {}).get("first_name", "") + " " +
                               (o.get("customer") or {}).get("last_name", "")).strip() or "Anonyme",
                    "country": cc,
                    "amount": float(o.get("total_price", 0)),
                    "status": o.get("financial_status", ""),
                })
        top = sorted([{"name": k, **v} for k, v in products.items()], key=lambda x: -x["qty"])[:10]
        return {
            "_live": True, "ca7": round(ca, 2), "orders7": len(orders),
            "basket": round(ca / len(orders), 2) if orders else 0,
            "to_ship": to_ship,
            "countries": [{"code": k, **v} for k, v in countries.items()],
            "top_products": top,
            "recent_orders": recent,
        }

    try:
        return _cached(f"shopify_{days}", _fetch, ttl=120)
    except (urlerr.HTTPError, urlerr.URLError, Exception) as e:
        return {"_live": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)
