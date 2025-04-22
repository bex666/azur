import os
import json
import undetected_chromedriver as uc
from services.location import get_current_location

CONFIG_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'config', 'browser_config.json')
)

USER_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'config', 'chrome_user_data')
)

BROWSER_KEY = 'chrome'

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)
    print(f"✅ Sauvegardé dans {CONFIG_FILE}")

def main():
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    print("🛠️ Configuration du navigateur avec undetected-chromedriver (Chrome uniquement)")
    cfg = load_config()
    binary = cfg.get('binary')

    default = '/usr/bin/google-chrome'

    if binary:
        print(f"Navigateur configuré : Chrome ({binary})")
    else:
        print(f"Aucun navigateur configuré. Utilisation du chemin par défaut : {default}")
        binary = default
        cfg = {'type': BROWSER_KEY, 'binary': binary}
        save_config(cfg)

    if not os.path.isfile(binary):
        print(f"❌ Fichier non trouvé : {binary}")
        return

    print("\n🔍 Test de lancement du navigateur Chrome...")
    try:
        loc = get_current_location()
        lat = loc.get('lat')
        lon = loc.get('lon')

        options = uc.ChromeOptions()
        options.binary_location = binary
        options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        options.add_argument("--profile-directory=Default")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1
        })

        driver = uc.Chrome(options=options)

        if lat and lon:
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": lat,
                "longitude": lon,
                "accuracy": 100
            })
            print(f"📡 Géolocalisation simulée : {lat}, {lon}")
        else:
            print("⚠️ Coordonnées GPS manquantes")

        print("✅ Chrome lancé avec succès via undetected-chromedriver.")
        maps_url = "https://www.google.com/maps"
        driver.get(maps_url)

        input("\nAppuyez sur Entrée pour fermer le navigateur et revenir au menu...")
        driver.quit()
    except Exception as e:
        print(f"⚠️ Échec du lancement ou de l'ouverture : {e}")

    print("\n🌍 Localisation simulée :")
    print(f" Ville : {loc.get('city','-')}")
    print(f" Pays  : {loc.get('country','-')}")
    print(f" Lat   : {loc.get('lat','-')}")
    print(f" Lon   : {loc.get('lon','-')}")
