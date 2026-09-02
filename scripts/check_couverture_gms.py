"""GARDE-FOU COUVERTURE GMS (REGLES §14) — Nicolas 02/09/2026.

Regle absolue posee par Nicolas :
    « On ne peut pas avoir un client pro GMS qui n'est jamais visite ni appele
      parce qu'il est trop loin des tournees. »
    « Soit tu arrives a le caser dans le prochain planning, si pas, d'office il
      doit etre dans televente. »

Il n'y a donc que DEUX issues, jamais « on verra la semaine prochaine » :
  1. le magasin est dans le planning merch de la semaine  -> rien a faire ;
  2. il n'y est pas -> bascule d'office en televente.

Le script compare les magasins sans contact depuis trop longtemps aux pids
reellement planifies (extraits de scripts/planning_data.py) et ecrit les
bascules dans data/force_televente_auto.json, relu par build_televente_pool.py.
Les magasins ainsi bascules sont PRIORITAIRES d'office dans la file d'appels :
ils ont deja ete oublies une fois.

FORCE_MERCH_PIDS prime : une decision explicite de Nicolas n'est jamais
ecrasee par l'automatisme.

Usage:
    python scripts/check_couverture_gms.py              # constat seul
    python scripts/check_couverture_gms.py --apply      # applique les bascules
    ... [AAAA-MM-JJ] [--semaines s36,s37]
"""
import csv, glob, json, re, sys, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
AUTO_FILE = DATA / "force_televente_auto.json"
PLANNING_DATA = REPO / "scripts" / "planning_data.py"

# Seuils (REGLES §14)
SEUIL_CRITIQUE = 45   # j sans contact -> bascule si non planifie
SEUIL_ALERTE   = 30   # j sans contact -> signale
ISOLEMENT_ZIP  = 2    # <= N magasins merch partageant les 2 premiers chiffres du
                      # code postal => magasin ISOLE (le merch n'ira pas)

PID_RE = re.compile(r"#(\d{3,6})")
SEM_RE = re.compile(r"^(S\d+)\s*=\s*\{", re.MULTILINE)

# FORCE_MERCH_PIDS prime sur l'automatisme : ces magasins ne PEUVENT pas basculer
# (build_televente_pool.py les exclut du pool Vanessa). Les signaler au lieu
# d'ecrire une bascule qui n'aurait aucun effet -> arbitrage manuel de Nicolas.
sys.path.insert(0, str(REPO / "scripts"))
try:
    from build_televente_pool import FORCE_MERCH_PIDS
except ImportError as e:                                  # pragma: no cover
    print(f"[!] FORCE_MERCH_PIDS illisible ({e}) -> conflits non detectes")
    FORCE_MERCH_PIDS = set()


def latest(pattern):
    files = sorted(glob.glob(str(DATA / pattern)))
    return Path(files[-1]) if files else None


def pids_planifies(semaines=None):
    """pids presents dans planning_data.py. Par defaut : les 2 dernieres semaines
    definies (semaine en cours + suivante)."""
    if not PLANNING_DATA.exists():
        print(f"[!] {PLANNING_DATA.name} introuvable -> aucun magasin considere planifie")
        return set(), []
    txt = PLANNING_DATA.read_text(encoding="utf-8")
    blocs = list(SEM_RE.finditer(txt))
    if not blocs:
        return set(), []
    noms = [m.group(1) for m in blocs]
    if semaines:
        keep = {s.upper() for s in semaines}
        sel = [(m, n) for m, n in zip(blocs, noms) if n in keep]
    else:
        sel = list(zip(blocs, noms))[-2:]
    pids = set()
    for i, (m, _) in enumerate(sel):
        start = m.start()
        idx = noms.index(sel[i][1])
        end = blocs[idx + 1].start() if idx + 1 < len(blocs) else len(txt)
        pids |= {int(p) for p in PID_RE.findall(txt[start:end])}
    return pids, [n for _, n in sel]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply_ = "--apply" in sys.argv
    semaines = None
    for a in sys.argv[1:]:
        if a.startswith("--semaines"):
            semaines = a.split("=", 1)[1].split(",") if "=" in a else None
    today = datetime.date.fromisoformat(args[0]) if args else datetime.date.today()

    fm, ft = latest("planning_pool_*.csv"), latest("televente_pool_*.csv")
    if not fm:
        sys.exit("[X] aucun planning_pool_*.csv — lance build_planning_pool.py d'abord")
    merch = list(csv.DictReader(fm.open(encoding="utf-8")))
    tele = list(csv.DictReader(ft.open(encoding="utf-8"))) if ft else []
    tele_pids = {r["pid"] for r in tele}
    planned, sem_noms = pids_planifies(semaines)
    print(f"[*] merch={fm.name} ({len(merch)})  televente={ft.name if ft else '-'} ({len(tele)})")
    print(f"[*] planning lu : {', '.join(sem_noms) or '-'} -> {len(planned)} magasin(s) planifie(s)\n")

    dens = {}
    for r in merch:
        if r["statut"] == "Actif":
            z = (r["zip"] or "")[:2]
            dens[z] = dens.get(z, 0) + 1

    alertes, bascules, bloques = [], {}, []
    for r in merch:
        if r["statut"] != "Actif" or r["pid"] in tele_pids:
            continue
        lv = r.get("last_visit") or ""
        sans = (today - datetime.date.fromisoformat(lv)).days if lv else 999
        if sans < SEUIL_ALERTE:
            continue
        pid = int(r["pid"])
        zone = (r["zip"] or "")[:2]
        isole = dens.get(zone, 0) <= ISOLEMENT_ZIP
        critique = sans >= SEUIL_CRITIQUE
        au_planning = pid in planned

        if critique and not au_planning and pid in FORCE_MERCH_PIDS:
            issue = ("BLOQUE — en FORCE_MERCH, ne peut pas basculer : "
                     "le caser au planning ou retirer de FORCE_MERCH_PIDS")
            bloques.append((pid, r["display_name"], sans))
        elif critique and not au_planning:
            issue = "BASCULE TELEVENTE"
            motif = (f"sans visite depuis {sans}j"
                     + (" — magasin isolé" if isole else "")
                     + " — non casé au planning")
            bascules[pid] = {"motif": motif, "depuis": lv or "jamais",
                             "jours": sans, "date_bascule": today.isoformat(),
                             "magasin": r["display_name"], "isole": isole}
        elif critique:
            issue = "planifié cette semaine — OK"
            motif = ""
        else:
            issue = "à surveiller"
            motif = ""

        alertes.append({
            "niveau": "CRITIQUE" if critique else "ALERTE", "pid": r["pid"],
            "magasin": r["display_name"], "zip": r["zip"], "city": r["city"],
            "tier": r["tier"], "last_visit": lv or "jamais",
            "jours_sans_contact": sans, "retard_j": r["retard_j"],
            "avg_mois": r["avg_mois"], "isole": "oui" if isole else "non",
            "au_planning": "oui" if au_planning else "non", "issue": issue,
        })

    alertes.sort(key=lambda a: (a["niveau"] != "CRITIQUE", -a["jours_sans_contact"]))
    if not alertes:
        print(f"[OK] Aucun magasin GMS actif sans contact depuis plus de {SEUIL_ALERTE} jours.")
        return

    print(f"{'niv':9} {'pid':8} {'zip':6} {'sans':>5} {'CA/m':>7} {'planning':>9}  magasin")
    for a in alertes:
        print(f"{a['niveau']:9} {a['pid']:8} {a['zip']:6} {a['jours_sans_contact']:4}j "
              f"{a['avg_mois']:>7} {a['au_planning']:>9}  {a['magasin'][:36]}")
        if a["issue"] != "à surveiller":
            print(f"{'':9} -> {a['issue']}")

    out = DATA / f"alertes_couverture_{today.isoformat()}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(alertes[0].keys()))
        w.writeheader(); w.writerows(alertes)
    print(f"\n[>] {out}")

    if bloques:
        print(f"\n[!] {len(bloques)} magasin(s) BLOQUE(S) en FORCE_MERCH — arbitrage manuel :")
        for pid, nom, sans in sorted(bloques, key=lambda b: -b[2]):
            print(f"    {pid:7} {nom[:40]:40} {sans}j sans visite")
        print("    -> les caser au planning, ou les retirer de FORCE_MERCH_PIDS.")

    if not bascules:
        print("\n[OK] Aucune bascule : tous les critiques sont au planning.")
        return

    ca = sum(float(a["avg_mois"] or 0) for a in alertes if int(a["pid"]) in bascules)
    print(f"\n[!] {len(bascules)} magasin(s) a basculer d'office en televente "
          f"({ca:,.0f} EUR/mois) :")
    for pid, b in sorted(bascules.items(), key=lambda kv: -kv[1]["jours"]):
        print(f"    {pid:7} {b['magasin'][:40]:40} {b['motif']}")

    if not apply_:
        print("\nDRY-RUN — relancer avec --apply pour ecrire les bascules.")
        return

    existing = {}
    if AUTO_FILE.exists():
        existing = json.loads(AUTO_FILE.read_text(encoding="utf-8"))
    existing.update({str(k): v for k, v in bascules.items()})
    AUTO_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"\n[>] {AUTO_FILE} ({len(existing)} magasin(s) en bascule auto)")
    print("[>] relance build_televente_pool.py puis build_televente_page.py")


if __name__ == "__main__":
    main()
