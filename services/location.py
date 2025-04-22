import json
import os

CONFIG_PATH = "config/location.json"

def get_current_location():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"city": "Paris", "country": "France"}

def choose_location():
    city = input("🏙️ Entre une ville à simuler : ")
    country = input("🌐 Pays : ")
    data = {"city": city, "country": country}
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"✅ Ville enregistrée : {city}, {country}")