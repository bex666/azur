import os
import json
import time
import requests

CACHE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'ip_info_cache.json'))
CACHE_TTL = 3600
IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')

def _load_cache():
    if not os.path.isfile(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r') as f:
            cached = json.load(f)
        if time.time() - cached.get('timestamp', 0) < CACHE_TTL:
            return cached.get('data')
    except:
        return None
    return None

def _save_cache(data):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({'timestamp': time.time(), 'data': data}, f)
    except:
        pass

def get_ip_info(force_refresh=False, verbose=False):
    if not force_refresh:
        cached = _load_cache()
        if cached:
            return cached
    url = 'https://ipinfo.io/json' + (f'?token={IPINFO_TOKEN}' if IPINFO_TOKEN else '')
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        result = {
            'ip': data.get('ip'),
            'tor': bool(data.get('privacy', {}).get('tor') or data.get('privacy', {}).get('proxy')),
            'geo': {k: data.get(k) for k in ('city','region','country','loc','org')},
            'alert': ''
        }
        _save_cache(result)
        return result
    except Exception as e:
        return {'ip': None, 'tor': False, 'geo': {}, 'alert': str(e)}
