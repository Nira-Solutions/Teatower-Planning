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
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)
