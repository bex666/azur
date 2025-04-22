import os
import json
import time
import requests

# Fichier de cache pour éviter les appels répétés
CACHE_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'config', 'ip_info_cache.json')
)
CACHE_TTL = 3600
IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')

def _load_cache():
    if not os.path.isfile(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cached = json.load(f)
        if time.time() - cached.get('timestamp', 0) < CACHE_TTL:
            print("🔄 Chargement des infos IP depuis le cache local.")
            return cached.get('data')
    except:
        return None
    return None

def _save_cache(data):
    try:
        tmp = {'timestamp': time.time(), 'data': data}
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(tmp, f)
        print("💾 Infos IP mises en cache.")
    except:
        pass

def get_ip_info(force_refresh=False, verbose=False):
    if not force_refresh:
        cached = _load_cache()
        if cached:
            if verbose:
                print("✅ Utilisation du cache.")
            return cached
    elif verbose:
        print("⚠️ Ignoring cache, fetching fresh info.")

    url = 'https://ipinfo.io/json'
    if IPINFO_TOKEN:
        url += f'?token={IPINFO_TOKEN}'
    if verbose:
        print(f"🌐 Requête vers : {url}")

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if verbose:
            print("📥 Réponse:", data)

        ip = data.get('ip')
        geo = {
            'city': data.get('city'),
            'region': data.get('region'),
            'country': data.get('country'),
            'loc': data.get('loc'),
            'org': data.get('org'),
        }
        privacy = data.get('privacy', {})
        tor_flag = bool(privacy.get('tor') or privacy.get('proxy'))

        result = {'ip': ip, 'tor': tor_flag, 'geo': geo, 'alert': ''}
        if verbose:
            print(f"🔍 IP: {ip}, Localisation: {geo['city']}, {geo['region']}, {geo['country']}, TOR: {tor_flag}")
        _save_cache(result)
        return result

    except Exception as e:
        alert = f"Erreur ipinfo: {e}"
        if verbose:
            print(f"❌ {alert}")
        return {'ip': None, 'tor': False, 'geo': {}, 'alert': alert}
