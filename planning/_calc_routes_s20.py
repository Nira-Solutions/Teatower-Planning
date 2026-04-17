"""
Calculate real travel times for Planning S20 (20-24 April 2026) using OSRM API.
Generates Google Maps links for each day's route.
Rules: VISITE = 30 min, IMPLANTATION = 1h, return Baillonville <= 16:30
"""
import urllib.request
import json
import time

# ── Locations (lat, lon) ──────────────────────────────────────────────
# Geocoded from Belgian addresses
LOCS = {
    "Baillonville":       (50.3340, 5.2830),
    # Monday
    "Delhaize Enghien":   (50.6908, 3.9647),
    "ITM Gosselies":      (50.4621, 4.4310),
    "ITM Floriffoux":     (50.4550, 4.7380),
    "ITM Spy":            (50.4793, 4.6670),
    "ITM Genappe":        (50.6108, 4.4492),
    "Crf Express Lasne":  (50.6867, 4.4867),
    # Tuesday
    "Spar Namur":         (50.4645, 4.8670),
    "Delhaize Bouge":     (50.4740, 4.8830),
    "ITM Bouge":          (50.4720, 4.8785),
    "ITM Naninne":        (50.4305, 4.8740),
    "ITM Belgrade":       (50.4480, 4.8540),
    "ITM Jambes":         (50.4530, 4.8710),
    "ITM Assesse":        (50.3800, 5.0100),
    "Spar Manhay":        (50.2880, 5.6750),
    # Wednesday
    "Hyper Boncelles":    (50.5810, 5.5300),
    "ITM Tilff":          (50.5650, 5.5850),
    "Hyper Fleron":       (50.6210, 5.6850),
    "Delhaize Barchon":   (50.6680, 5.7420),
    "Delhaize Bois-de-breux": (50.6450, 5.6260),
    "ITM Herve":          (50.6390, 5.7940),
    "Delhaize Liege Ardente": (50.6380, 5.5870),
    "Proxy Saint-Severin": (50.5060, 5.4150),
    "AD Fosses-la-Ville": (50.3955, 4.6970),
    # Thursday
    "CM Beauraing":       (50.1100, 4.9570),
    "Delhaize Beauraing": (50.1085, 4.9580),
    "AD Rochefort":       (50.1600, 5.2220),
    "ITM Anhee":          (50.3100, 4.8750),
    "Proxy Ferrieres":    (50.3930, 5.6130),
    "Delhaize Ottignies": (50.5810, 4.5150),  # Villers-La-Ville
    "CM Hannut":          (50.6710, 5.0790),
    # Friday
    "CM Bievre":          (49.9350, 5.0200),
    "Proxy Maissin":      (49.9460, 5.1460),
    "AD Bastogne":        (50.0000, 5.7150),
    "CM Bastogne":        (50.0020, 5.7100),
    "CM Hotton":          (50.2670, 5.4460),
    "Delhaize Barvaux":   (50.3530, 5.4940),
    "Delhaize Marche":    (50.2270, 5.3440),
    "CM Barvaux":         (50.3550, 5.4920),  # to be removed
}


def osrm_route(coords_list):
    """Query OSRM for route through a list of (lat, lon) tuples.
    Returns list of segment durations in minutes and total distance in km."""
    # OSRM uses lon,lat format
    coords_str = ";".join(f"{lon},{lat}" for lat, lon in coords_list)
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=false&steps=false&annotations=false"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Teatower-Planning/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        if data.get("code") != "Ok":
            return None, None, None

        route = data["routes"][0]
        legs = route["legs"]
        durations = [leg["duration"] / 60 for leg in legs]  # seconds -> minutes
        distances = [leg["distance"] / 1000 for leg in legs]  # meters -> km
        total_duration = route["duration"] / 60
        total_distance = route["distance"] / 1000
        return durations, distances, total_distance
    except Exception as e:
        print(f"  ERROR: {e}")
        return None, None, None


def google_maps_link(stops):
    """Generate Google Maps directions link for a list of stop names."""
    coords = [LOCS[s] for s in stops]
    origin = f"{coords[0][0]},{coords[0][1]}"
    dest = f"{coords[-1][0]},{coords[-1][1]}"
    waypoints = "|".join(f"{lat},{lon}" for lat, lon in coords[1:-1])
    if waypoints:
        return f"https://www.google.com/maps/dir/{'/'.join(f'{lat},{lon}' for lat, lon in coords)}"
    else:
        return f"https://www.google.com/maps/dir/{origin}/{dest}"


def calc_day(day_name, stops_with_type, start_time_h=8.5):
    """
    stops_with_type: list of (stop_name, type) where type is 'IMPLANTATION' or 'VISITE'
    VISITE = 30 min, IMPLANTATION = 60 min
    start_time_h: start time in decimal hours (8.5 = 08:30)
    """
    stop_names = ["Baillonville"] + [s[0] for s in stops_with_type] + ["Baillonville"]
    coords = [LOCS[s] for s in stop_names]

    print(f"\n{'='*70}")
    print(f"  {day_name}")
    print(f"{'='*70}")

    durations, distances, total_dist = osrm_route(coords)
    if durations is None:
        print("  ERREUR: impossible de calculer la route")
        return

    # Build schedule
    current_time = start_time_h  # decimal hours
    schedule = []

    for i, (stop_name, stop_type) in enumerate(stops_with_type):
        travel_min = durations[i]
        travel_km = distances[i]
        on_site_min = 60 if stop_type == "IMPLANTATION" else 30

        arrival = current_time + travel_min / 60
        departure = arrival + on_site_min / 60

        schedule.append({
            "stop": stop_name,
            "type": stop_type,
            "travel_from_prev_min": round(travel_min),
            "travel_from_prev_km": round(travel_km, 1),
            "arrival": arrival,
            "departure": departure,
            "on_site_min": on_site_min,
        })

        current_time = departure

    # Return trip
    return_travel_min = durations[-1]
    return_travel_km = distances[-1]
    return_time = current_time + return_travel_min / 60

    # Print schedule
    for s in schedule:
        arr_h = int(s["arrival"])
        arr_m = int((s["arrival"] - arr_h) * 60)
        dep_h = int(s["departure"])
        dep_m = int((s["departure"] - dep_h) * 60)
        print(f"  {arr_h:02d}:{arr_m:02d}-{dep_h:02d}:{dep_m:02d} | {s['type']:14s} | {s['stop']}")
        print(f"           trajet: {s['travel_from_prev_min']} min ({s['travel_from_prev_km']} km)")

    ret_h = int(return_time)
    ret_m = int((return_time - ret_h) * 60)
    print(f"\n  Retour Baillonville: {ret_h:02d}:{ret_m:02d} (trajet: {round(return_travel_min)} min, {round(return_travel_km, 1)} km)")
    print(f"  Distance totale: {round(total_dist)} km")

    if return_time > 16.5:
        print(f"  ** DEPASSEMENT ! Retour {ret_h:02d}:{ret_m:02d} > 16:30 **")
    else:
        margin = (16.5 - return_time) * 60
        print(f"  OK -- marge: {round(margin)} min avant 16h30")

    # Google Maps link
    link = google_maps_link(stop_names)
    print(f"\n  Google Maps: {link}")

    return schedule, return_time, total_dist


print("=" * 70)
print("PLANNING S20 — SIMULATION TRAJETS RÉELS (OSRM)")
print("=" * 70)

# ── LUNDI 20/04 ──
calc_day("LUNDI 20/04 — Hainaut + Namur", [
    ("Delhaize Enghien", "IMPLANTATION"),  # 1h
    ("ITM Gosselies", "VISITE"),
    ("ITM Floriffoux", "VISITE"),
    ("ITM Spy", "VISITE"),
    ("ITM Genappe", "VISITE"),
    ("Crf Express Lasne", "VISITE"),
])
time.sleep(1)  # rate limit OSRM

# ── MARDI 21/04 ──
# Correction: Spar Manhay (Lambertdis) = IMPLANTATION (1h)
calc_day("MARDI 21/04 — Namur (Lambertis = IMPLANTATION)", [
    ("Spar Namur", "IMPLANTATION"),  # 1h
    ("Delhaize Bouge", "VISITE"),
    ("ITM Bouge", "VISITE"),
    ("ITM Naninne", "VISITE"),
    ("ITM Belgrade", "VISITE"),
    ("ITM Jambes", "VISITE"),
    ("ITM Assesse", "VISITE"),
    ("Spar Manhay", "IMPLANTATION"),  # CORRECTION: IMPLANTATION 1h
])
time.sleep(1)

# ── MARDI 21/04 — VARIANTE SANS MANHAY ──
print("\n\n>>> VARIANTE MARDI SANS MANHAY (si trop loin) <<<")
calc_day("MARDI 21/04 — VARIANTE sans Manhay", [
    ("Spar Namur", "IMPLANTATION"),
    ("Delhaize Bouge", "VISITE"),
    ("ITM Bouge", "VISITE"),
    ("ITM Naninne", "VISITE"),
    ("ITM Belgrade", "VISITE"),
    ("ITM Jambes", "VISITE"),
    ("ITM Assesse", "VISITE"),
])
time.sleep(1)

# ── MERCREDI 22/04 ──
calc_day("MERCREDI 22/04 — Liège + Fosses-la-Ville", [
    ("Hyper Boncelles", "VISITE"),
    ("ITM Tilff", "VISITE"),
    ("Hyper Fleron", "VISITE"),
    ("Delhaize Barchon", "VISITE"),
    ("Delhaize Bois-de-breux", "VISITE"),
    ("ITM Herve", "VISITE"),
    ("Delhaize Liege Ardente", "VISITE"),
    ("Proxy Saint-Severin", "VISITE"),
    ("AD Fosses-la-Ville", "VISITE"),
])
time.sleep(1)

# ── MERCREDI 22/04 — VARIANTE SANS FOSSES ──
print("\n\n>>> VARIANTE MERCREDI SANS FOSSES (si trop loin) <<<")
calc_day("MERCREDI 22/04 — VARIANTE sans Fosses", [
    ("Hyper Boncelles", "VISITE"),
    ("ITM Tilff", "VISITE"),
    ("Hyper Fleron", "VISITE"),
    ("Delhaize Barchon", "VISITE"),
    ("Delhaize Bois-de-breux", "VISITE"),
    ("ITM Herve", "VISITE"),
    ("Delhaize Liege Ardente", "VISITE"),
    ("Proxy Saint-Severin", "VISITE"),
])
time.sleep(1)

# ── JEUDI 23/04 ──
calc_day("JEUDI 23/04 — Namur sud + Ferrières + BW", [
    ("CM Beauraing", "VISITE"),
    ("Delhaize Beauraing", "VISITE"),
    ("AD Rochefort", "VISITE"),
    ("ITM Anhee", "VISITE"),
    ("Proxy Ferrieres", "VISITE"),
    ("Delhaize Ottignies", "VISITE"),
    ("CM Hannut", "VISITE"),
])
time.sleep(1)

# ── JEUDI 23/04 — VARIANTE sans Ferrières (route bizarre) ──
print("\n\n>>> VARIANTE JEUDI SANS FERRIERES <<<")
calc_day("JEUDI 23/04 — VARIANTE sans Ferrières", [
    ("CM Beauraing", "VISITE"),
    ("Delhaize Beauraing", "VISITE"),
    ("AD Rochefort", "VISITE"),
    ("ITM Anhee", "VISITE"),
    ("Delhaize Ottignies", "VISITE"),
    ("CM Hannut", "VISITE"),
])
time.sleep(1)

# ── VENDREDI 24/04 ── (CM Barvaux RETIRÉ — visité la semaine passée)
calc_day("VENDREDI 24/04 — Namur sud / Luxembourg (SANS CM Barvaux)", [
    ("CM Bievre", "IMPLANTATION"),
    ("Proxy Maissin", "IMPLANTATION"),
    ("AD Bastogne", "VISITE"),
    ("CM Bastogne", "VISITE"),
    ("CM Hotton", "VISITE"),
    ("Delhaize Barvaux", "VISITE"),  # Delhaize Barvaux (Gilles) kept, CM Barvaux removed
    ("Delhaize Marche", "VISITE"),
])

print("\n\nDONE — Use results above to rebuild the planning.")
