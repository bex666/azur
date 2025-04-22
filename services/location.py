import os, json, random

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'location.json'))

CITIES = [
    {"city": "Paris", "country": "France", "lat": 48.8566, "lon": 2.3522},
    {"city": "Lyon", "country": "France", "lat": 45.7640, "lon": 4.8357},
    {"city": "Marseille", "country": "France", "lat": 43.2965, "lon": 5.3698},
    {"city": "Toulouse", "country": "France", "lat": 43.6047, "lon": 1.4442},
    {"city": "Nice", "country": "France", "lat": 43.7102, "lon": 7.2620},
]

def get_current_location(force_city_index=None):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if all(k in data for k in ('city', 'country', 'lat', 'lon')):
                return data
    except Exception:
        pass

    if force_city_index is not None and 0 <= force_city_index < len(CITIES):
        return CITIES[force_city_index]

    return random.choice(CITIES)

def set_city_by_index(index):
    if 0 <= index < len(CITIES):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(CITIES[index], f, indent=2)
        print(f"✅ Ville enregistrée : {CITIES[index]['city']}, {CITIES[index]['country']}")
    else:
        print("❌ Index invalide.")

def city_selection_cli():
    print("\n🏙️ Choisissez une ville :")
    for i, city in enumerate(CITIES, 1):
        print(f" {i}. {city['city']}, {city['country']}")
    try:
        choice = int(input("Votre choix (1-5) : ")) - 1
        set_city_by_index(choice)
    except ValueError:
        print("❌ Entrée invalide.")
