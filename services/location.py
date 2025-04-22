import os
import json

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'location.json'))

def get_current_location():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'city':'Unknown','country':'Unknown'}
