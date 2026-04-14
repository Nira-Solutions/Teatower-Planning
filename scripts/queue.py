#!/usr/bin/env python3
"""
Mise à jour de data/nira_queue.json — file de travail affichée sur agents_dashboard.html.

Usage :
  python scripts/queue.py start  --agent planning    --task "Planning S17"       --request "Nira → ..."
  python scripts/queue.py done   --id t042           [--task "..."]
  python scripts/queue.py add    --agent compta      --task "..."  --status pending --request "..."

Après chaque modif : git add + commit + push automatique (repo public via GitHub Pages).
"""
import argparse, json, subprocess, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "data" / "nira_queue.json"

def now():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")

def load():
    if not QUEUE.exists():
        return {"updated": now(), "tasks": []}
    return json.loads(QUEUE.read_text(encoding="utf-8"))

def save(data):
    data["updated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    QUEUE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def next_id(tasks):
    nums = [int(t["id"][1:]) for t in tasks if t["id"].startswith("t") and t["id"][1:].isdigit()]
    return f"t{(max(nums) + 1) if nums else 1:03d}"

def git_push(message):
    try:
        subprocess.run(["git", "-C", str(ROOT), "add", "data/nira_queue.json"], check=True)
        subprocess.run(["git", "-C", str(ROOT), "commit", "-m", message], check=True)
        subprocess.run(["git", "-C", str(ROOT), "push"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[queue] git push échoué : {e}", file=sys.stderr)

def cmd_start(args):
    data = load()
    tid = next_id(data["tasks"])
    data["tasks"].append({
        "id": tid, "agent": args.agent, "task": args.task,
        "status": "in_progress", "started": now(), "request": args.request or ""
    })
    save(data)
    git_push(f"Queue: {args.agent} start — {args.task[:60]}")
    print(tid)

def cmd_done(args):
    data = load()
    for t in data["tasks"]:
        if t["id"] == args.id:
            t["status"] = "done"
            t["finished"] = now()
            if args.task: t["task"] = args.task
            break
    else:
        print(f"[queue] id inconnu: {args.id}", file=sys.stderr); sys.exit(1)
    save(data)
    git_push(f"Queue: done {args.id}")

def cmd_add(args):
    data = load()
    tid = next_id(data["tasks"])
    entry = {"id": tid, "agent": args.agent, "task": args.task,
             "status": args.status, "started": now() if args.status == "in_progress" else None,
             "request": args.request or ""}
    if args.status == "done":
        entry["finished"] = now()
    data["tasks"].append(entry)
    save(data)
    git_push(f"Queue: {args.agent} {args.status} — {args.task[:60]}")
    print(tid)

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start"); s.add_argument("--agent", required=True); s.add_argument("--task", required=True); s.add_argument("--request", default="")
    s.set_defaults(func=cmd_start)

    s = sub.add_parser("done"); s.add_argument("--id", required=True); s.add_argument("--task", default=None)
    s.set_defaults(func=cmd_done)

    s = sub.add_parser("add"); s.add_argument("--agent", required=True); s.add_argument("--task", required=True); s.add_argument("--status", default="pending", choices=["pending","in_progress","done"]); s.add_argument("--request", default="")
    s.set_defaults(func=cmd_add)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
