# interface/cli.py
import importlib
import os
import pkgutil
from services.location import get_current_location
from services.ip_info import get_ip_info

MODULE_PATH = "services"

def discover_modules():
    print("\n🔍 Modules disponibles dans 'services/' :")
    modules = []
    for finder, name, ispkg in pkgutil.iter_modules([MODULE_PATH]):
        modules.append(name)
    return sorted(modules)

def start_cli():
    ip_info = get_ip_info(force_refresh=True)

    while True:
        location = get_current_location()

        print("\n🧠 Bienvenue dans SGL – Search Google Legitimately")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🌍 Ville simulée : {location['city']}, {location['country']}")
        print(f"🌐 IP publique : {ip_info['ip']}  |  TOR : {'Oui' if ip_info['tor'] else 'Non'}")
        if ip_info.get("alert"):
            print(ip_info["alert"])
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        modules = discover_modules()
        for i, module in enumerate(modules, 1):
            print(f"{i}. 📦 {module}")
        print(f"{len(modules)+1}. ❌ Quitter")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        try:
            choice = int(input("🔀 Choisis un module à exécuter : "))
        except ValueError:
            print("❌ Entrée invalide. Donne un chiffre.")
            continue

        if 1 <= choice <= len(modules):
            module_name = modules[choice - 1]
            print(f"▶️ Lancement du module '{module_name}'...")
            try:
                mod = importlib.import_module(f"services.{module_name}")
                if hasattr(mod, "main"):
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
