import os
import json
import undetected_chromedriver as uc
from services.location import get_current_location

# Chemin du fichier de config pour le navigateur
CONFIG_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'config', 'browser_config.json')
)

# Seul navigateur supporté
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
    # Création du fichier de configuration s'il n'existe pas
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    print("🛠️ Configuration du navigateur avec undetected-chromedriver (Chrome uniquement)")
    cfg = load_config()
    binary = cfg.get('binary')

    # Chemin par défaut
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

    # Test de lancement via undetected-chromedriver
    print("\n🔍 Test de lancement du navigateur Chrome...")
    try:
        options = uc.ChromeOptions()
        options.binary_location = binary
        driver = uc.Chrome(options=options)
        print("✅ Chrome lancé avec succès via undetected-chromedriver.")

        # Ouverture automatique de Google Maps à la localisation simulée
        loc = get_current_location()
        query = f"{loc.get('city','')},{loc.get('country','')}"
        maps_url = f"https://www.google.com/maps/search/?api=1&query={query}"
        print(f"🌐 Ouverture de Google Maps pour : {query}")
        driver.get(maps_url)

        # Laisser le navigateur ouvert jusqu'à une entrée utilisateur
        input("\nAppuyez sur Entrée pour fermer le navigateur et revenir au menu...")
        driver.quit()
    except Exception as e:
        print(f"⚠️ Échec du lancement ou de l'ouverture : {e}")

    # Affichage de la localisation simulée
    print("\n🌍 Localisation simulée :")
    loc = get_current_location()
    print(f" Ville : {loc.get('city','-')}")
    print(f" Pays  : {loc.get('country','-')}")
