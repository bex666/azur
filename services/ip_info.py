import os
import json
import time
import requests
import subprocess

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
            return cached.get('data')
    except:
        return None
    return None

def _save_cache(data):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': time.time(), 'data': data}, f)
    except:
        pass

def get_ip_info(force_refresh=False, verbose=False):
    if not force_refresh:
        cached = _load_cache()
        if cached:
            return cached
    url = 'https://ipinfo.io/json' + (f'?token={IPINFO_TOKEN}' if IPINFO_TOKEN else '')
    resp = requests.get(url, timeout=5); resp.raise_for_status()
    d = resp.json()
    info = {
        'ip': d.get('ip'),
        'tor': bool(d.get('privacy', {}).get('tor') or d.get('privacy', {}).get('proxy')),
        'geo': {k: d.get(k) for k in ('city','region','country','loc','org')},
        'alert': ''
    }
    _save_cache(info)
    return info

def main():
    try:
        info = get_ip_info(force_refresh=True)
    except Exception as e:
        print(f"⚠️ Erreur récupération IP : {e}")
        return

    print("🌐 IP Publique :", info.get('ip','N/A'))
    print("🛡️ TOR         :", "Oui" if info.get('tor') else "Non")
    geo = info.get('geo', {})
    print("📍 Ville       :", geo.get('city','-'))
    print("   Région      :", geo.get('region','-'))
    print("   Pays        :", geo.get('country','-'))
    print("📡 Coordonnées  :", geo.get('loc','-'))
    print("🏢 Fournisseur :", geo.get('org','-'))
    if info.get('alert'):
        print("⚠️ Alerte      :", info['alert'])

    # Ping test
    try:
        print("⏳ Test ping vers 8.8.8.8...")
        r = subprocess.run(['ping','-c','4','8.8.8.8'], capture_output=True, text=True, check=True)
        for line in r.stdout.splitlines():
            if 'rtt' in line:
                avg = line.split(' = ')[1].split('/')[1]
                print(f"📶 Ping moyen : {avg} ms")
                break
    except Exception as e:
        print(f"⚠️ Ping impossible : {e}")
