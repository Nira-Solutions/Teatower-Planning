#!/usr/bin/env python3
"""Backfill historique XP agents — simule leurs tâches passées."""
import json, datetime as dt, random, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "data" / "nira_queue.json"

HIST = {
    "odoo": ("Debug flux Odoo", 80),
    "planning":      ("Planning merchandiser semaine", 50),
    "support-order": ("Devis client Odoo",            45),
    "compta":        ("Facturation / lettrage",       40),
    "purchase":      ("Analyse achats / PO Kirchner", 35),
    "stock-manager": ("Orderpoints min/max magasin",  30),
    "merchandiser":  ("Upload visite merchandiser",   25),
    "sales-crm":     ("Enrichissement fiche CRM",     2),
}

SAMPLES = {
    "odoo": ["Debug ir.cron {mod}", "Script XML-RPC {mod}", "Correction vue {mod}",
             "Automation {mod}", "Champ custom {mod}", "Intégration Shopify", "Migration données {mod}",
             "Diagnostic perf {mod}", "Setup route GMS", "Fix séquence {mod}"],
    "planning": ["Planning S{n}", "Implantation {c}", "Réassort +3 sem {c}", "Urgence {c}"],
    "support-order": ["Devis {c} S0{n}", "Update fiche partner {c}", "Attachement PDF S0{n}"],
    "compta": ["Facture {c}", "Lettrage paiement {c}", "Balance âgée", "Forecast J+30"],
    "purchase": ["Import PO Kirchner {n}", "Analyse retard {c}", "Maj prix fournisseur {c}",
                 "Maj délai supplierinfo {c}"],
    "stock-manager": ["Orderpoint {c} WAT", "Orderpoint {c} LIEGE", "Transfert TT→WAT",
                      "Analyse réappro {c}"],
    "merchandiser": ["Upload visite {c}", "BC magasin {c}"],
    "sales-crm": ["Lead {c}", "Relance {c}"],
}

CLIENTS = ["Delhaize Waterloo","Carrefour Ciney","Spar Manhay","Intermarché Jambes",
           "Lambertdis","Match Liège","Louis Delhaize","Colruyt","AD Gembloux",
           "Radisson","Smartbox","Noé Nature","Kirchner","Dethlefsen","Mount Everest"]
MODS = ["sale","purchase","stock","account","product","res.partner","mrp","account.move",
        "ir.cron","mail.mail","stock.picking","product.supplierinfo","crm.lead"]

def load():
    return json.loads(QUEUE.read_text(encoding="utf-8"))

def save(data):
    QUEUE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def gen(agent, n):
    existing_ids = set()
    samples = SAMPLES[agent]
    now = dt.datetime.now()
    tasks = []
    for i in range(n):
        # répartir sur 120 derniers jours
        days_ago = random.uniform(0.5, 120)
        started = now - dt.timedelta(days=days_ago)
        dur = random.randint(4, 90)
        finished = started + dt.timedelta(minutes=dur)
        sample = random.choice(samples)
        task = sample.format(
            c=random.choice(CLIENTS),
            mod=random.choice(MODS),
            n=random.randint(100, 9999),
        )
        tid = f"h_{agent[:3]}_{i:03d}"
        tasks.append({
            "id": tid,
            "agent": agent,
            "task": task,
            "status": "done",
            "started": started.strftime("%Y-%m-%dT%H:%M"),
            "finished": finished.strftime("%Y-%m-%dT%H:%M"),
            "request": f"historique simulé (agent {agent})"
        })
    return tasks

def main():
    random.seed(42)
    data = load()
    # garde les tasks live (non h_*)
    live = [t for t in data["tasks"] if not t["id"].startswith("h_")]
    hist = []
    for agent, (_, n) in HIST.items():
        hist += gen(agent, n)
    data["tasks"] = hist + live
    data["updated"] = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    save(data)
    print(f"✓ {len(hist)} tasks historiques ajoutées · {len(live)} tasks live conservées")
    # XP récap
    from collections import Counter
    c = Counter(t["agent"] for t in data["tasks"] if t["status"] == "done")
    import math
    for a, n in c.most_common():
        xp = n * 10
        lvl = 1 + int(math.sqrt(xp / 25))
        print(f"  {a:16} {n:3} done · {xp:4} XP · LVL {lvl}")

if __name__ == "__main__":
    main()
