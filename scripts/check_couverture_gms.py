"""GARDE-FOU COUVERTURE GMS (REGLES §13) — Nicolas 02/09/2026.

Regle absolue posee par Nicolas :
    « On ne peut pas avoir un client pro GMS qui n'est jamais visite ni appele
      parce qu'il est trop loin des tournees. »

Le cas Delhaize Ath (#123144) : bon client (431 EUR/mois reel), reste dans le
pool merch semaine apres semaine avec un retard croissant, mais n'est jamais
retenu dans une tournee car il est le seul magasin du pool en Hainaut
occidental. Personne ne le voit -> 2 mois sans contact.

Ce script se lance APRES build_planning_pool.py et build_televente_pool.py.
Il croise les deux pools et sort tout magasin qui n'est couvert par AUCUN des
deux, ou couvert sur le papier mais jamais servi dans les faits.

Sortie : console + data/alertes_couverture_<date>.csv
Code retour 1 si au moins une alerte CRITIQUE -> visible dans un enchainement.

Usage: python scripts/check_couverture_gms.py [AAAA-MM-JJ]
"""
import csv, glob, sys, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

# Seuils (REGLES §13)
SEUIL_CRITIQUE = 45   # j sans contact -> CRITIQUE, arbitrage obligatoire
SEUIL_ALERTE   = 30   # j sans contact -> a surveiller
ISOLEMENT_ZIP  = 2    # nb de magasins merch partageant les 2 premiers chiffres du
                      # code postal en dessous duquel on considere le magasin ISOLE


def latest(pattern):
    files = sorted(glob.glob(str(DATA / pattern)))
    return Path(files[-1]) if files else None


def main():
    today = (datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1
             else datetime.date.today())

    fm, ft = latest("planning_pool_*.csv"), latest("televente_pool_*.csv")
    if not fm:
        sys.exit("[X] aucun planning_pool_*.csv — lance build_planning_pool.py d'abord")
    merch = list(csv.DictReader(fm.open(encoding="utf-8")))
    tele = list(csv.DictReader(ft.open(encoding="utf-8"))) if ft else []
    tele_pids = {r["pid"] for r in tele}
    print(f"[*] merch={fm.name} ({len(merch)})  televente={ft.name if ft else '-'} ({len(tele)})\n")

    # densite merch par prefixe de code postal (zone a 2 chiffres)
    dens = {}
    for r in merch:
        if r["statut"] == "Actif":
            dens[(r["zip"] or "")[:2]] = dens.get((r["zip"] or "")[:2], 0) + 1

    alertes = []
    for r in merch:
        if r["statut"] not in ("Actif",):
            continue
        if r["pid"] in tele_pids:
            continue                      # couvert par Vanessa, rien a signaler
        retard = int(r["retard_j"] or 0)
        lv = r.get("last_visit") or ""
        sans_contact = (today - datetime.date.fromisoformat(lv)).days if lv else 999
        if sans_contact < SEUIL_ALERTE:
            continue
        zone = (r["zip"] or "")[:2]
        isole = dens.get(zone, 0) <= ISOLEMENT_ZIP
        niveau = "CRITIQUE" if sans_contact >= SEUIL_CRITIQUE else "ALERTE"
        if isole:
            reco = (f"ISOLE ({dens.get(zone,0)} magasin(s) merch en zone {zone}xxx) "
                    f"-> basculer en TELEVENTE (FORCE_TELEVENTE_PIDS)")
        else:
            reco = f"zone {zone}xxx couverte ({dens.get(zone,0)} magasins) -> a caler dans la prochaine tournee"
        alertes.append({
            "niveau": niveau, "pid": r["pid"], "magasin": r["display_name"],
            "zip": r["zip"], "city": r["city"], "tier": r["tier"],
            "cycle_days": r["cycle_days"], "last_visit": lv or "jamais",
            "jours_sans_contact": sans_contact, "retard_j": retard,
            "avg_mois": r["avg_mois"], "isole": "oui" if isole else "non",
            "recommandation": reco,
        })

    alertes.sort(key=lambda a: (a["niveau"] != "CRITIQUE", -a["jours_sans_contact"]))
    crit = [a for a in alertes if a["niveau"] == "CRITIQUE"]

    if not alertes:
        print("[OK] Aucun magasin GMS actif sans contact depuis plus de "
              f"{SEUIL_ALERTE} jours.")
    else:
        print(f"{'niv':9} {'pid':8} {'zip':6} {'sans contact':>13} {'retard':>7} {'CA/m':>6}  magasin")
        for a in alertes:
            print(f"{a['niveau']:9} {a['pid']:8} {a['zip']:6} {a['jours_sans_contact']:11}j "
                  f"{a['retard_j']:6}j {a['avg_mois']:>6}  {a['magasin'][:38]}")
            print(f"{'':9} -> {a['recommandation']}")

    out = DATA / f"alertes_couverture_{today.isoformat()}.csv"
    if alertes:
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(alertes[0].keys()))
            w.writeheader(); w.writerows(alertes)
        print(f"\n[>] {out}")

    if crit:
        print(f"\n[!] {len(crit)} magasin(s) CRITIQUE(s) : arbitrage OBLIGATOIRE "
              f"(visite cette semaine / bascule televente / arret).")
        sys.exit(1)


if __name__ == "__main__":
    main()
