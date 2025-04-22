# interface/cli.py
import os
import random
from services.navigator import HumanNavigator
from services.location import choose_location, get_current_location
from services.ip_info import get_ip_info
from services.browser_test import run_browser_check

KEYWORDS_PATH = "config/mots_cles.txt"

def load_keywords():
    if not os.path.exists(KEYWORDS_PATH):
        print("⚠️ Fichier de mots-clés introuvable. Utilisation des mots-clés par défaut.")
        return ["actualités", "musique", "films"]
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
    if not keywords:
        print("⚠️ Le fichier de mots-clés est vide. Utilisation des mots-clés par défaut.")
        return ["actualités", "musique", "films"]
    return keywords

def handle_static_session():
    print("🧊 Lancement de session statique...")
    keywords = load_keywords()
    nav = HumanNavigator()
    try:
        for _ in range(3):
            kw = random.choice(keywords)
            print(f"🔍 Recherche: {kw}")
            nav.search(kw)
            nav.open_first_result_in_new_tab()
    finally:
        nav.close()

def handle_dynamic_session():
    print("▶️ Lancement de session dynamique...")
    # TODO: Implémenter les trajets, POI, navigation contextuelle, etc.
    pass

def handle_edit_keywords():
    print("✏️ Édition des mots-clés...")
    os.system(f"nano {KEYWORDS_PATH}")

def handle_network_info():
    ip_info = get_ip_info(force_refresh=True)
    print("\nℹ️ Détails réseau :")
    print(f"🔎 Adresse IP : {ip_info['ip']}")
    print(f"🛡️ TOR activé : {'Oui' if ip_info['tor'] else 'Non'}")
    if ip_info.get("alert"):
        print(ip_info["alert"])
    geo = ip_info['geo']
    print(f"📍 Localisation IP : {geo['city']}, {geo['region']}, {geo['country']}")
    print(f"🏢 Fournisseur : {geo['org']}")
    print(f"🧭 Coordonnées : {geo['loc']}")

def handle_browser_config():
    while True:
        print("\n🧩 CONFIGURATION NAVIGATEUR")
        print("1. ✅ Vérification automatique (Google Maps, fermeture auto)")
        print("2. 👁️ Vérifier manuellement (ouvre Maps, tu fermes toi-même)")
        print("3. ↩️ Retour au menu")
        choice = input("👉 Choix : ").strip()

        if choice == "1":
            run_browser_check(auto_close=True)
            break
        elif choice == "2":
            run_browser_check(auto_close=False)
            break
        elif choice == "3":
            break
        else:
            print("❌ Choix invalide. Essaie encore.")

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
        print("🔎 RECHERCHE")
        print("1. ▶️ Lancer une session dynamique")
        print("2. 🧊 Lancer une session statique")
        print("3. ⏰ Planifier une session")
        print("\n⚙️ CONFIGURATION")
        print("4. 🌍 Changer de ville")
        print("5. 🧩 Configurer le navigateur et vérifier la localisation")
        print("6. ✏️ Modifier les mots-clés")
        print("7. ℹ️ Voir les détails réseau")
        print("8. ❌ Quitter")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        choice = input("🔀 Que veux-tu faire ? ")

        if choice == "1":
            handle_dynamic_session()
        elif choice == "2":
            handle_static_session()
        elif choice == "3":
            print("⏰ [TODO] Planification...")
        elif choice == "4":
            choose_location()
        elif choice == "5":
            handle_browser_config()
        elif choice == "6":
            handle_edit_keywords()
        elif choice == "7":
            handle_network_info()
        elif choice == "8":
            print("👋 À bientôt.")
            break
        else:
            print("❌ Option invalide. Essaie encore.")