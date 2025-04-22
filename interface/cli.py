import importlib
import os
import pkgutil
import json
import textwrap
from services.location import get_current_location as real_get_current_location
from services.ip_info import get_ip_info

# Pour colorer la sortie (nécessite pip install colorama)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        BLUE = ''
        GREEN = ''
        CYAN = ''
        YELLOW = ''
        RED = ''
        MAGENTA = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''

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
    all_mods = discover_modules()
    statics = [m for _, m in STATIC_MODULES]
    remaining = [m for m in all_mods if m not in statics]
    rest = [(m, m) for m in remaining]
    menu = []
    for title, group in CATEGORIES:
        entries = rest if title == "Modules restants" else group
        menu.append((title, entries))
    return menu

def print_header(sim_loc, ip_info):
    header = f" SGL – Search Google Legitimately "
    width = 60
    print(Fore.BLUE + Style.BRIGHT + header.center(width, '=') + Style.RESET_ALL)
    loc_str = f"🌍 {sim_loc.get('city','?')}, {sim_loc.get('country','?')}"
    ip_str = f"🌐 {ip_info.get('ip','N/A')} | TOR: {'Oui' if ip_info.get('tor') else 'Non'}"
    print(Fore.CYAN + loc_str.ljust(width//2) + ip_str.rjust(width//2))
    geo = ip_info.get('geo', {})
    if geo:
        geo_str = f"📍 {geo.get('city','?')}, {geo.get('region','?')}, {geo.get('country','?')}"
        print(Fore.CYAN + geo_str.center(width))
    if ip_info.get('alert'):
        print(Fore.RED + ip_info['alert'].center(width))
    print('=' * width)

def print_keywords(keywords):
    if not keywords:
        return
    print(Fore.YELLOW + "🗒️ Mots-clés :" + Style.RESET_ALL)
    print(textwrap.fill(', '.join(keywords), width=60))
    print('-' * 60)

def start_cli():
    config_location = load_config_location()
    keywords = load_keywords()
    ip_info = get_ip_info(force_refresh=True, verbose=False)

    while True:
        sim_loc = config_location or real_get_current_location()
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header(sim_loc, ip_info)
        print_keywords(keywords)

        menu = build_menu()
        choices = {}
        idx = 1
        for title, entries in menu:
            print(Fore.MAGENTA + Style.BRIGHT + f"{title}" + Style.RESET_ALL)
            for label, module in entries:
                print(f" {Fore.GREEN}{idx}{Style.RESET_ALL}. {label}")
                choices[idx] = module
                idx += 1
            print()
        print(f" {Fore.RED}{idx}{Style.RESET_ALL}. Quitter")
        print('=' * 60)

        try:
            choice = int(input(Fore.CYAN + "🔀 Votre choix: " + Style.RESET_ALL))
        except ValueError:
            continue

        if choice == idx:
            print(Fore.YELLOW + "👋 À bientôt !")
            break
        module = choices.get(choice)
        if not module:
            continue

        print(Fore.BLUE + f"\n▶️ Exécution du module: {module}\n" + Style.RESET_ALL)
        try:
            mod = importlib.import_module(f"services.{module}")
            mod.main()
        except Exception as e:
            print(Fore.RED + f"Erreur: {e}")
        input(Fore.CYAN + "\nAppuyez sur Entrée pour revenir au menu...")
