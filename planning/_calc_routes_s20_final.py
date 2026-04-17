"""
Final route checks for S20 v5 planning
"""
import urllib.request, json, time

LOCS = {
    "Baillonville": (50.3340, 5.2830),
    "Delhaize Enghien": (50.6908, 3.9647),
    "ITM Gosselies": (50.4621, 4.4310),
    "ITM Floriffoux": (50.4550, 4.7380),
    "ITM Spy": (50.4793, 4.6670),
    "AD Fosses-la-Ville": (50.3955, 4.6970),
    "ITM Anhee": (50.3100, 4.8750),
    "CM Beauraing": (50.1100, 4.9570),
    "Delhaize Beauraing": (50.1085, 4.9580),
    "AD Rochefort": (50.1600, 5.2220),
    "Proxy Ferrieres": (50.3930, 5.6130),
    "CM Hannut": (50.6710, 5.0790),
    "Delhaize Ottignies": (50.5810, 4.5150),
    "Spar Namur": (50.4645, 4.8670),
    "Delhaize Bouge": (50.4740, 4.8830),
    "ITM Bouge": (50.4720, 4.8785),
    "ITM Naninne": (50.4305, 4.8740),
    "ITM Belgrade": (50.4480, 4.8540),
    "ITM Assesse": (50.3800, 5.0100),
    "Spar Manhay": (50.2880, 5.6750),
}


def osrm_route(coords_list):
    coords_str = ";".join(f"{lon},{lat}" for lat, lon in coords_list)
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=false&steps=false"
    req = urllib.request.Request(url, headers={"User-Agent": "Teatower-Planning/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    route = data["routes"][0]
    legs = route["legs"]
    durations = [leg["duration"] / 60 for leg in legs]
    distances = [leg["distance"] / 1000 for leg in legs]
    return durations, distances, route["distance"] / 1000


def calc_day(day_name, stops_with_type, start_time_h=8.5):
    stop_names = ["Baillonville"] + [s[0] for s in stops_with_type] + ["Baillonville"]
    coords = [LOCS[s] for s in stop_names]
    durations, distances, total_dist = osrm_route(coords)

    print(f"\n{'='*70}")
    print(f"  {day_name}")
    print(f"{'='*70}")

    current_time = start_time_h
    for i, (stop_name, stop_type) in enumerate(stops_with_type):
        travel_min = durations[i]
        travel_km = distances[i]
        on_site_min = 60 if stop_type == "IMPLANTATION" else 30
        arrival = current_time + travel_min / 60
        departure = arrival + on_site_min / 60
        ah, am = int(arrival), int((arrival % 1) * 60)
        dh, dm = int(departure), int((departure % 1) * 60)
        print(f"  {ah:02d}:{am:02d}-{dh:02d}:{dm:02d} | {stop_type:14s} | {stop_name} ({round(travel_min)}min, {round(travel_km,1)}km)")
        current_time = departure

    return_time = current_time + durations[-1] / 60
    rh, rm = int(return_time), int((return_time % 1) * 60)
    print(f"\n  Retour: {rh:02d}:{rm:02d} | {round(total_dist)}km total | {len(stops_with_type)} stops")
    if return_time > 16.5:
        print(f"  ** DEPASSEMENT **")
    else:
        print(f"  OK -- marge: {round((16.5-return_time)*60)} min")

    link = "https://www.google.com/maps/dir/" + "/".join(f"{LOCS[s][0]},{LOCS[s][1]}" for s in stop_names)
    print(f"  Maps: {link}")
    return return_time


# Test 1: LUNDI avec Fosses (pas mardi = OK, preference mercredi mais pas obligatoire)
print(">>> TEST: LUNDI avec Fosses-la-Ville apres Spy")
calc_day("LUNDI — Enghien + Gosselies + Spy + Fosses + Floriffoux", [
    ("Delhaize Enghien", "IMPLANTATION"),
    ("ITM Gosselies", "VISITE"),
    ("ITM Spy", "VISITE"),
    ("AD Fosses-la-Ville", "VISITE"),
    ("ITM Floriffoux", "VISITE"),
])
time.sleep(0.5)

print("\n>>> TEST: LUNDI Enghien + Gosselies + Spy + Floriffoux + Fosses")
calc_day("LUNDI — Enghien/Gosselies/Spy/Floriffoux/Fosses (Fosses en dernier)", [
    ("Delhaize Enghien", "IMPLANTATION"),
    ("ITM Gosselies", "VISITE"),
    ("ITM Spy", "VISITE"),
    ("ITM Floriffoux", "VISITE"),
    ("AD Fosses-la-Ville", "VISITE"),
])
time.sleep(0.5)

# Test 2: JEUDI Anhee-Beauraing-Rochefort-Ferrieres-Hannut
print("\n>>> TEST: JEUDI route optimale sud + Ferrieres + Hannut")
calc_day("JEUDI — Anhee/Beauraing/Rochefort/Ferrieres/Hannut", [
    ("ITM Anhee", "VISITE"),
    ("CM Beauraing", "VISITE"),
    ("Delhaize Beauraing", "VISITE"),
    ("AD Rochefort", "VISITE"),
    ("Proxy Ferrieres", "VISITE"),
    ("CM Hannut", "VISITE"),
])
time.sleep(0.5)

# Test 3: JEUDI sans Hannut (Hannut sur un autre jour)
print("\n>>> TEST: JEUDI route sud + Ferrieres + Ottignies (au lieu de Hannut)")
calc_day("JEUDI — Anhee/Beauraing/Rochefort/Ferrieres/Ottignies", [
    ("Delhaize Ottignies", "VISITE"),
    ("ITM Anhee", "VISITE"),
    ("CM Beauraing", "VISITE"),
    ("Delhaize Beauraing", "VISITE"),
    ("AD Rochefort", "VISITE"),
    ("Proxy Ferrieres", "VISITE"),
])
time.sleep(0.5)

# Test 4: MARDI avec Fosses en premier (avant Namur)
print("\n>>> TEST: MARDI Fosses + Namur + Manhay")
calc_day("MARDI — Fosses/Namur/Manhay", [
    ("AD Fosses-la-Ville", "VISITE"),
    ("Spar Namur", "IMPLANTATION"),
    ("Delhaize Bouge", "VISITE"),
    ("ITM Bouge", "VISITE"),
    ("ITM Naninne", "VISITE"),
    ("ITM Belgrade", "VISITE"),
    ("ITM Assesse", "VISITE"),
    ("Spar Manhay", "IMPLANTATION"),
])
time.sleep(0.5)

# Test 5: JEUDI Ottignies + Hannut + magasins zone (journee BW)
print("\n>>> TEST: JEUDI Fosses + Ottignies + Hannut")
calc_day("JEUDI — Fosses/Ottignies/Hannut", [
    ("AD Fosses-la-Ville", "VISITE"),
    ("Delhaize Ottignies", "VISITE"),
    ("CM Hannut", "VISITE"),
])

print("\n=== DONE ===")
