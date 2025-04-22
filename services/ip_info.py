import os
import json
import time
import requests
import subprocess

# Fichier de cache pour éviter les appels répétés
CACHE_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'config', 'ip_info_cache.json')
)
# Durée de vie du cache en secondes (1 heure)
CACHE_TTL = 3600
# Jeton d'accès pour ipinfo.io (optionnel)
IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')


def _load_cache():
    """Charge les données mises en cache si non expirées."""
    if not os.path.isfile(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cached = json.load(f)
        if time.time() - cached.get('timestamp', 0) < CACHE_TTL:
            return cached.get('data')
    except Exception:
        return None
    return None


def _save_cache(data):
    """Sauvegarde les données dans le cache avec timestamp."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': time.time(), 'data': data}, f)
    except Exception:
        pass


def get_ip_info(force_refresh=False, verbose=False):
    """
    Récupère l'IP publique et géolocalisation via ipinfo.io, avec cache.
    """
    if not force_refresh:
        cached = _load_cache()
        if cached:
            return cached

    url = 'https://ipinfo.io/json'
    if IPINFO_TOKEN:
        url += f'?token={IPINFO_TOKEN}'

    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()

    info = {
        'ip': data.get('ip'),
        'tor': bool(data.get('privacy', {}).get('tor') or data.get('privacy', {}).get('proxy')),
        'geo': {
            'city': data.get('city'),
            'region': data.get('region'),
            'country': data.get('country'),
            'loc': data.get('loc'),
            'org': data.get('org'),
        },
        'alert': ''
    }
    _save_cache(info)
    return info


def main():
    """Point d'entrée CLI pour afficher les infos IP et ping."""
    try:
        info = get_ip_info(force_refresh=True)
    except Exception as e:
        print(f"⚠️ Erreur récupération IP : {e}")
        return

    # Affichage des données IP
    print("🌐 IP Publique :", info.get('ip', 'N/A'))
    print("🛡️ TOR         :", "Oui" if info.get('tor') else "Non")
    geo = info.get('geo', {})
    print("📍 Ville       :", geo.get('city', '-'))
    print("   Région      :", geo.get('region', '-'))
    print("   Pays        :", geo.get('country', '-'))
    print("📡 Coordonnées  :", geo.get('loc', '-'))
    print("🏢 Fournisseur :", geo.get('org', '-'))
    if info.get('alert'):
        print("⚠️ Alerte      :", info['alert'])

    # Test de ping vers Google DNS
    try:
        print("⏳ Test ping vers 8.8.8.8...")
        result = subprocess.run([
            'ping', '-c', '4', '8.8.8.8'
        ], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if 'rtt min/avg' in line or 'round-trip min/avg' in line:
                stats = line.split(' = ')[1].split(' ')[0]
                avg = stats.split('/')[1]
                print(f"📶 Ping moyen : {avg} ms")
                break
    except Exception as e:
        print(f"⚠️ Ping impossible : {e}")
