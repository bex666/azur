import importlib
import os
import pkgutil
import json
from services.location import get_current_location as real_get_current_location
from services.ip_info import get_ip_info

# Configuration paths
dir_here = os.path.dirname(__file__)
CONFIG_DIR = os.path.abspath(os.path.join(dir_here, '..', 'config'))
LOCATION_CONF = os.path.join(CONFIG_DIR, 'location.json')
KEYWORDS_CONF = os.path.join(CONFIG_DIR, 'mot_cles.txt')
MODULE_PATH = "services"

# Définition des catégories et modules statiques
STATIC_MODULES = [
    ("Recherche statique", "recherche_statique"),
    ("Recherche mobile", "recherche_mobile"),
    ("Recherche planifiée", "recherche_planifiee"),
    ("Choix de la ville", "location"),
    ("Configuration du navigateur + vérification de la localisation", "browser_config"),
    ("IP", "ip_info"),
    ("Module en test", "module_test"),
]
CATEGORIES = [
    ("Recherche", STATIC_MODULES[:3]),
    ("Configuration", STATIC_MODULES[3:5]),
    ("Infos", STATIC_MODULES[5:6]),
    ("Module en test", STATIC_MODULES[6:7]),
    ("Modules restants", None),  # sera rempli dynamiquement
]


def load_config_location():
    try:
        with open(LOCATION_CONF, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_keywords():
    try:
        with open(KEYWORDS_CONF, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def discover_modules():
    modules = []
    for _, name, _ in pkgutil.iter_modules([MODULE_PATH]):
        modules.append(name)
    return sorted(modules)


def build_menu():
    # Modules dynamiques restants
    all_mods = discover_modules()
    statics = [m for _, m in STATIC_MODULES]
    remaining = [m for m in all_mods if m not in statics]
    # Remplir la catégorie "Modules restants"
    rest = [(m, m) for m in remaining]
    menu = []
    for title, group in CATEGORIES:
        if title == "Modules restants":
            entries = rest
        else:
            entries = group
        menu.append((title, entries))
    return menu


def start_cli():
    config_location = load_config_location()
    keywords = load_keywords()
    # IP au démarrage
    ip_info = get_ip_info(force_refresh=True, verbose=True)

    while True:
        # Localisation
        sim_loc = config_location or real_get_current_location()

        # En-tête
        print(f"\n🧠 SGL – Search Google Legitimately")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🌍 Localisation simulée : {sim_loc.get('city','?')}, {sim_loc.get('country','?')}")
        print(f"🌐 IP publique : {ip_info.get('ip','N/A')}  |  TOR : {'Oui' if ip_info.get('tor') else 'Non'}")
        geo = ip_info.get('geo', {})
        if geo:
            print(f"📍 Géo-IP : {geo.get('city','?')}, {geo.get('region','?')}, {geo.get('country','?')}")
        if ip_info.get('alert'):
            print(f"⚠️ Alerte : {ip_info['alert']}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Mots-clés
        if keywords:
            print("🗒️ Mots-clés :", ', '.join(keywords))
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Construction du menu
        menu = build_menu()
        index = 1
        choices = {}
        for title, entries in menu:
            print(f"{title} :")
            for label, module in entries:
                print(f"  {index}. {label}")
                choices[index] = module
                index += 1
        print(f"  {index}. ❌ Quitter")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Sélection
        try:
            choice = int(input("🔀 Sélectionnez une option : "))
        except ValueError:
            print("❌ Entrée invalide.")
            continue

        if choice == index:
            print("👋 À bientôt.")
            break
        module_name = choices.get(choice)
        if not module_name:
            print("❌ Option invalide.")
            continue

        # Exécution du module
        print(f"▶️ Exécution du module '{module_name}'...")
        try:
            mod = importlib.import_module(f"services.{module_name}")
            if hasattr(mod, 'main'):
                mod.main()
            else:
                print("⚠️ Module sans 'main()'.")
        except Exception as e:
            print(f"💥 Erreur : {e}")
