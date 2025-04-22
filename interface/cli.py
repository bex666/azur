import importlib
import os
import pkgutil
import json
from services.location import get_current_location as real_get_current_location
from services.ip_info import get_ip_info

# Configuration paths
BASE_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'config'))
LOCATION_CONF = os.path.join(CONFIG_DIR, 'location.json')
KEYWORDS_CONF = os.path.join(CONFIG_DIR, 'mot_cles.txt')
MODULE_PATH = "services"


def load_config_location():
    """
    Charge la configuration de localisation depuis config/location.json.
    """
    try:
        with open(LOCATION_CONF, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_keywords():
    """
    Charge la liste de mots-clés depuis config/mot_cles.txt.
    """
    try:
        with open(KEYWORDS_CONF, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def discover_modules():
    """
    Découvre dynamiquement les modules Python dans le dossier services/.
    """
    modules = []
    for _, name, _ in pkgutil.iter_modules([MODULE_PATH]):
        modules.append(name)
    return sorted(modules)


def start_cli():
    # Chargement des configs
    config_location = load_config_location()
    keywords = load_keywords()

    # Récupération IP (verbose pour logs détaillés)
    ip_info = get_ip_info(force_refresh=True, verbose=True)

    while True:
        # Localisation simulée vs réelle
        if config_location:
            sim_loc = config_location
            source = 'config'
        else:
            sim_loc = real_get_current_location()
            source = 'API locale'

        # En-tête
        print("\n🧠 Bienvenue dans SGL – Search Google Legitimately")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🔧 Source localisation simulée : {source}")
        print(f"🌍 Localisation simulée : {sim_loc.get('city','?')}, {sim_loc.get('country','?')}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Affichage de l'IP et géo-réalité
        print(f"🌐 IP publique : {ip_info.get('ip', 'N/A')}  |  TOR : {'Oui' if ip_info.get('tor') else 'Non'}")
        geo = ip_info.get('geo', {})
        if geo:
            print(f"📍 Localisation IP : {geo.get('city','?')}, {geo.get('region','?')}, {geo.get('country','?')}")
            print(f"📡 Coordonnées : {geo.get('loc','?')}")
            print(f"🏢 Fournisseur : {geo.get('org','?')}")
        if ip_info.get('alert'):
            print(f"⚠️ Alerte : {ip_info['alert']}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Affichage des mots-clés configurés
        if keywords:
            print("🗒️ Mots-clés configurés :")
            for kw in keywords:
                print(f" - {kw}")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Liste des modules disponibles
        modules = discover_modules()
        for i, module in enumerate(modules, 1):
            print(f"{i}. 📦 {module}")
        print(f"{len(modules)+1}. ❌ Quitter")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Choix utilisateur
        try:
            choice = int(input("🔀 Choisis un module à exécuter : "))
        except ValueError:
            print("❌ Entrée invalide. Donne un chiffre.")
            continue

        # Exécution ou sortie
        if 1 <= choice <= len(modules):
            module_name = modules[choice - 1]
            print(f"▶️ Lancement du module '{module_name}'...")
            try:
                mod = importlib.import_module(f"services.{module_name}")
                if hasattr(mod, 'main'):
                    mod.main()
                else:
                    print("⚠️ Ce module n'a pas de fonction 'main()'.")
            except Exception as e:
                print(f"💥 Erreur dans le module : {e}")
        elif choice == len(modules) + 1:
            print("👋 À bientôt.")
            break
        else:
            print("❌ Option invalide.")
