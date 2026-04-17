"""
Planning S20 v5 — Routes corrigees avec OSRM
Corrections:
- Lambertis (Manhay) = IMPLANTATION 1h
- CM Barvaux retire (visite la semaine passee)
- Routes geographiquement coherentes
- Tous les trajets verifies OSRM
"""
import urllib.request
import json
import time

LOCS = {
    "Baillonville": (50.3340, 5.2830),
    # Monday
    "Delhaize Enghien": (50.6908, 3.9647),
    "ITM Gosselies": (50.4621, 4.4310),
    "ITM Floriffoux": (50.4550, 4.7380),
    "ITM Spy": (50.4793, 4.6670),
    "ITM Genappe": (50.6108, 4.4492),
    "Crf Express Lasne": (50.6867, 4.4867),
    # Tuesday
    "Spar Namur": (50.4645, 4.8670),
    "Delhaize Bouge": (50.4740, 4.8830),
    "ITM Bouge": (50.4720, 4.8785),
    "ITM Naninne": (50.4305, 4.8740),
    "ITM Belgrade": (50.4480, 4.8540),
    "ITM Jambes": (50.4530, 4.8710),
    "ITM Assesse": (50.3800, 5.0100),
    "Spar Manhay": (50.2880, 5.6750),
    "AD Fosses-la-Ville": (50.3955, 4.6970),
    # Wednesday
    "Hyper Boncelles": (50.5810, 5.5300),
    "ITM Tilff": (50.5650, 5.5850),
    "Hyper Fleron": (50.6210, 5.6850),
    "Delhaize Barchon": (50.6680, 5.7420),
    "Delhaize Bois-de-breux": (50.6450, 5.6260),
    "ITM Herve": (50.6390, 5.7940),
    "Delhaize Liege Ardente": (50.6380, 5.5870),
    "Proxy Saint-Severin": (50.5060, 5.4150),
    # Thursday
    "CM Beauraing": (50.1100, 4.9570),
    "Delhaize Beauraing": (50.1085, 4.9580),
    "AD Rochefort": (50.1600, 5.2220),
    "ITM Anhee": (50.3100, 4.8750),
    "Proxy Ferrieres": (50.3930, 5.6130),
    "CM Hannut": (50.6710, 5.0790),
    "Delhaize Ottignies": (50.5810, 4.5150),
    # Friday
    "CM Bievre": (49.9350, 5.0200),
    "Proxy Maissin": (49.9460, 5.1460),
    "AD Bastogne": (50.0000, 5.7150),
    "CM Bastogne": (50.0020, 5.7100),
    "CM Hotton": (50.2670, 5.4460),
    "Delhaize Barvaux": (50.3530, 5.4940),
    "Delhaize Marche": (50.2270, 5.3440),
}


def osrm_route(coords_list):
    coords_str = ";".join(f"{lon},{lat}" for lat, lon in coords_list)
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=false&steps=false"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Teatower-Planning/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        if data.get("code") != "Ok":
            return None, None, None
        route = data["routes"][0]
        legs = route["legs"]
        durations = [leg["duration"] / 60 for leg in legs]
        distances = [leg["distance"] / 1000 for leg in legs]
        return durations, distances, route["distance"] / 1000
    except Exception as e:
        print(f"  ERROR: {e}")
        return None, None, None


def google_maps_link(stops):
    coords = [LOCS[s] for s in stops]
    return "https://www.google.com/maps/dir/" + "/".join(f"{lat},{lon}" for lat, lon in coords)


def calc_day(day_name, stops_with_type, start_time_h=8.5):
    stop_names = ["Baillonville"] + [s[0] for s in stops_with_type] + ["Baillonville"]
    coords = [LOCS[s] for s in stop_names]
    print(f"\n{'='*70}")
    print(f"  {day_name}")
    print(f"{'='*70}")

    durations, distances, total_dist = osrm_route(coords)
    if durations is None:
        print("  ERREUR: route impossible")
        return None

    current_time = start_time_h
    schedule = []
    for i, (stop_name, stop_type) in enumerate(stops_with_type):
        travel_min = durations[i]
        travel_km = distances[i]
        on_site_min = 60 if stop_type == "IMPLANTATION" else 30
        arrival = current_time + travel_min / 60
        departure = arrival + on_site_min / 60
        schedule.append({
            "stop": stop_name, "type": stop_type,
            "travel_min": round(travel_min), "travel_km": round(travel_km, 1),
            "arrival": arrival, "departure": departure, "on_site_min": on_site_min,
        })
        current_time = departure

    return_travel_min = durations[-1]
    return_travel_km = distances[-1]
    return_time = current_time + return_travel_min / 60

    for s in schedule:
        ah, am = int(s["arrival"]), int((s["arrival"] % 1) * 60)
        dh, dm = int(s["departure"]), int((s["departure"] % 1) * 60)
        print(f"  {ah:02d}:{am:02d}-{dh:02d}:{dm:02d} | {s['type']:14s} | {s['stop']}")
        print(f"           trajet depuis precedent: {s['travel_min']} min ({s['travel_km']} km)")

    rh, rm = int(return_time), int((return_time % 1) * 60)
    print(f"\n  Retour Baillonville: {rh:02d}:{rm:02d} (trajet retour: {round(return_travel_min)} min, {round(return_travel_km,1)} km)")
    print(f"  Distance totale: {round(total_dist)} km")
    print(f"  Nombre de stops: {len(stops_with_type)}")

    if return_time > 16.5:
        print(f"  ** DEPASSEMENT {rh:02d}:{rm:02d} > 16:30 **")
    else:
        margin = (16.5 - return_time) * 60
        print(f"  OK -- marge: {round(margin)} min avant 16h30")

    link = google_maps_link(stop_names)
    print(f"  Google Maps: {link}")
    return return_time


print("=" * 70)
print("PLANNING S20 v5 — SIMULATION OSRM CORRIGEE")
print("=" * 70)

# ── LUNDI 20/04 ──
# Enghien = 100 min, trop loin pour 6 stops. Max 4 stops apres Enghien.
# Option: Enghien + Gosselies + Floriffoux + Spy (4 stops, retour via Sambre)
print("\n>>> LUNDI — Option A: Enghien + 3 visites (Gosselies/Floriffoux/Spy)")
calc_day("LUNDI 20/04 — Option A (4 stops)", [
    ("Delhaize Enghien", "IMPLANTATION"),
    ("ITM Gosselies", "VISITE"),
    ("ITM Floriffoux", "VISITE"),
    ("ITM Spy", "VISITE"),
])
time.sleep(0.5)

# Option B: Enghien + Gosselies + Spy + Floriffoux (reordonne)
print("\n>>> LUNDI — Option B: Enghien + Gosselies + Spy + Floriffoux")
calc_day("LUNDI 20/04 — Option B (4 stops, ordre different)", [
    ("Delhaize Enghien", "IMPLANTATION"),
    ("ITM Gosselies", "VISITE"),
    ("ITM Spy", "VISITE"),
    ("ITM Floriffoux", "VISITE"),
])
time.sleep(0.5)

# ── MARDI 21/04 ──
# Manhay = IMPLANTATION 1h. Sans Jambes (doublon), ca devrait passer.
print("\n>>> MARDI — Namur + Manhay IMPLANTATION (sans Jambes)")
calc_day("MARDI 21/04 — sans Jambes, Manhay IMPLANTATION", [
    ("Spar Namur", "IMPLANTATION"),
    ("Delhaize Bouge", "VISITE"),
    ("ITM Bouge", "VISITE"),
    ("ITM Naninne", "VISITE"),
    ("ITM Belgrade", "VISITE"),
    ("ITM Assesse", "VISITE"),
    ("Spar Manhay", "IMPLANTATION"),
])
time.sleep(0.5)

# Variante: avec Jambes, sans Manhay (Manhay reporte)
print("\n>>> MARDI — Variante avec Jambes, sans Manhay")
calc_day("MARDI 21/04 — avec Jambes, sans Manhay", [
    ("Spar Namur", "IMPLANTATION"),
    ("Delhaize Bouge", "VISITE"),
    ("ITM Bouge", "VISITE"),
    ("ITM Naninne", "VISITE"),
    ("ITM Belgrade", "VISITE"),
    ("ITM Jambes", "VISITE"),
    ("ITM Assesse", "VISITE"),
])
time.sleep(0.5)

# ── MERCREDI 22/04 ──
# Fosses-la-Ville en PREMIER (proche Baillonville, ~45min), puis Liege
print("\n>>> MERCREDI — Fosses EN PREMIER puis Liege")
calc_day("MERCREDI 22/04 — Fosses d'abord, puis Liege", [
    ("AD Fosses-la-Ville", "VISITE"),
    ("Hyper Boncelles", "VISITE"),
    ("ITM Tilff", "VISITE"),
    ("Hyper Fleron", "VISITE"),
    ("Delhaize Barchon", "VISITE"),
    ("Delhaize Bois-de-breux", "VISITE"),
    ("ITM Herve", "VISITE"),
    ("Delhaize Liege Ardente", "VISITE"),
    ("Proxy Saint-Severin", "VISITE"),
])
time.sleep(0.5)

# Variante: Liege sans Fosses (Fosses reporte)
print("\n>>> MERCREDI — Sans Fosses (8 stops Liege)")
calc_day("MERCREDI 22/04 — Liege sans Fosses", [
    ("Hyper Boncelles", "VISITE"),
    ("ITM Tilff", "VISITE"),
    ("Hyper Fleron", "VISITE"),
    ("Delhaize Barchon", "VISITE"),
    ("Delhaize Bois-de-breux", "VISITE"),
    ("ITM Herve", "VISITE"),
    ("Delhaize Liege Ardente", "VISITE"),
    ("Proxy Saint-Severin", "VISITE"),
])
time.sleep(0.5)

# ── JEUDI 23/04 ──
# Route logique: Namur sud (Beauraing/Rochefort/Anhee) + Ferrieres + Hannut
# Sans Ottignies (BW, trop loin dans le zigzag)
print("\n>>> JEUDI — Namur sud + Ferrieres + Hannut (sans Ottignies)")
calc_day("JEUDI 23/04 — Beauraing/Rochefort/Anhee + Ferrieres + Hannut", [
    ("CM Beauraing", "VISITE"),
    ("Delhaize Beauraing", "VISITE"),
    ("AD Rochefort", "VISITE"),
    ("ITM Anhee", "VISITE"),
    ("Proxy Ferrieres", "VISITE"),
    ("CM Hannut", "VISITE"),
])
time.sleep(0.5)

# Variante: sans Hannut (Hannut trop au nord apres Ferrieres)
print("\n>>> JEUDI — Namur sud + Ferrieres (sans Hannut)")
calc_day("JEUDI 23/04 — Beauraing/Rochefort/Anhee/Ferrieres", [
    ("CM Beauraing", "VISITE"),
    ("Delhaize Beauraing", "VISITE"),
    ("AD Rochefort", "VISITE"),
    ("ITM Anhee", "VISITE"),
    ("Proxy Ferrieres", "VISITE"),
])
time.sleep(0.5)

# Variante: route coherente Beauraing/Rochefort + retour via Anhee + Ferrieres sur route Baillonville
print("\n>>> JEUDI — Beauraing/Rochefort/Anhee puis Ferrieres direct Baillonville")
calc_day("JEUDI 23/04 — Route sud puis Ferrieres", [
    ("ITM Anhee", "VISITE"),
    ("CM Beauraing", "VISITE"),
    ("Delhaize Beauraing", "VISITE"),
    ("AD Rochefort", "VISITE"),
    ("Proxy Ferrieres", "VISITE"),
])
time.sleep(0.5)

# Variante avec Ottignies + Hannut SEULS (journee BW/Hesbaye)
print("\n>>> JEUDI — Variante Ottignies + Hannut + Fosses")
calc_day("JEUDI 23/04 — Ottignies/Hannut/Fosses (journee BW)", [
    ("AD Fosses-la-Ville", "VISITE"),
    ("Delhaize Ottignies", "VISITE"),
    ("CM Hannut", "VISITE"),
])
time.sleep(0.5)

# ── VENDREDI 24/04 ──
# CM Barvaux RETIRE. 2 implantations + stops.
# Option sans Delhaize Marche (dernier stop qui fait depasser)
print("\n>>> VENDREDI — 2 implantations + Bastogne + Hotton + Barvaux (sans Marche)")
calc_day("VENDREDI 24/04 — sans Marche", [
    ("CM Bievre", "IMPLANTATION"),
    ("Proxy Maissin", "IMPLANTATION"),
    ("AD Bastogne", "VISITE"),
    ("CM Bastogne", "VISITE"),
    ("CM Hotton", "VISITE"),
    ("Delhaize Barvaux", "VISITE"),
])
time.sleep(0.5)

# Option: sans Barvaux ET sans Marche (plus court)
print("\n>>> VENDREDI — 2 implantations + Bastogne + Hotton + Marche (Marche avant Barvaux)")
calc_day("VENDREDI 24/04 — Bievre/Maissin/Bastogne/Hotton/Marche", [
    ("CM Bievre", "IMPLANTATION"),
    ("Proxy Maissin", "IMPLANTATION"),
    ("AD Bastogne", "VISITE"),
    ("CM Bastogne", "VISITE"),
    ("CM Hotton", "VISITE"),
    ("Delhaize Marche", "VISITE"),
])
time.sleep(0.5)

# Option: Hotton avant Bastogne (route differente)
print("\n>>> VENDREDI — Bievre/Maissin/Bastogne/Hotton/Barvaux/Marche complet")
calc_day("VENDREDI 24/04 — complet 7 stops", [
    ("CM Bievre", "IMPLANTATION"),
    ("Proxy Maissin", "IMPLANTATION"),
    ("AD Bastogne", "VISITE"),
    ("CM Bastogne", "VISITE"),
    ("CM Hotton", "VISITE"),
    ("Delhaize Barvaux", "VISITE"),
    ("Delhaize Marche", "VISITE"),
])

print("\n\n=== DONE ===")
