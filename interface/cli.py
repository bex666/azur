import importlib
import os
import pkgutil
import json
from services.location import get_current_location as real_get_current_location, city_selection_cli
from services.ip_info import get_ip_info

# Constantes
WIDTH = 60
MODULE_PATH = 'services'
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
LOCATION_CONF = os.path.join(CONFIG_DIR, 'location.json')
KEYWORDS_CONF = os.path.join(CONFIG_DIR, 'mot_cles.txt')

# Modules statiques et catégories
STATIC_MODULES = [
    ('Recherche statique', 'recherche_statique'),
    ('Recherche mobile', 'recherche_mobile'),
    ('Recherche planifiée', 'recherche_planifiee'),
    ('Choix de la ville', 'location'),
    ('Configuration navigateur', 'browser_config'),
    ('Éditer mots-clés', 'edit_keywords'),
    ('IP', 'ip_info'),
    ('Module en test', 'module_test'),
]
CATEGORIES = [
    ('🔍 Recherche', STATIC_MODULES[:3]),
    ('⚙️ Configuration', STATIC_MODULES[3:6]),
    ('ℹ️ Infos', STATIC_MODULES[6:7]),
    ('🧪 Module en test', STATIC_MODULES[7:8]),
    ('🧩 Modules restants', None),
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
    names = [name for _, name, _ in pkgutil.iter_modules([MODULE_PATH])]
    return sorted(names)

def build_menu():
    all_mods = discover_modules()
    static_keys = [m for _, m in STATIC_MODULES]
    dynamic = [m for m in all_mods if m not in static_keys]
    menu = []
    for title, group in CATEGORIES:
        if title == '🧩 Modules restants':
            entries = [(m, m) for m in dynamic]
        else:
            entries = group
        menu.append((title, entries))
    return menu

def print_header(sim_loc, ip_info):
    print(' ' + 'SGL – Search Google Legitimately'.center(WIDTH-2) + ' ')
    print('=' * WIDTH)
    loc = f"🌍 {sim_loc.get('city','?')}, {sim_loc.get('country','?')}"
    ip = f"🌐 {ip_info.get('ip','N/A')} | TOR: {'Oui' if ip_info.get('tor') else 'Non'}"
    print(loc.ljust(WIDTH//2) + ip.rjust(WIDTH//2))
    geo = ip_info.get('geo', {})
    if geo:
        geo_str = f"📍 {geo.get('city','?')}, {geo.get('region','?')}, {geo.get('country','?')}"
        print(geo_str.center(WIDTH))
    alert = ip_info.get('alert')
    if alert:
        print(alert.center(WIDTH))
    print('=' * WIDTH)

def print_keywords_count(keywords):
    print(f"🗒️ {len(keywords)} mots-clés configurés")
    print('-' * WIDTH)

def start_cli():
    config_loc = load_config_location()
    keywords = load_keywords()
    ip_info = get_ip_info(force_refresh=True)

    while True:
        sim_loc = config_loc or real_get_current_location()
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header(sim_loc, ip_info)
        print_keywords_count(keywords)

        menu = build_menu()
        choices = {}
        idx = 1
        for title, entries in menu:
            print(title)
            for label, module in entries:
                print(f" {idx}. {label}")
                choices[idx] = module
                idx += 1
            print()
        print(f" {idx}. Quitter")
        print('=' * WIDTH)

        try:
            choice = int(input("🔀 Votre choix: "))
        except ValueError:
            continue

        if choice == idx:
            print("👋 À bientôt !")
            break

        module = choices.get(choice)
        if not module:
            continue

        if module == 'edit_keywords':
            os.system(f'nano "{KEYWORDS_CONF}"')
            keywords = load_keywords()
            continue

        if module == 'location':
            city_selection_cli()
            config_loc = load_config_location()
            continue

        print(f"\n▶️ Exécution du module: {module}\n")
        try:
            mod = importlib.import_module(f"services.{module}")
            mod.main()
        except Exception as e:
            print(f"Erreur: {e}")
        input("\nAppuyez sur Entrée pour revenir au menu...")
