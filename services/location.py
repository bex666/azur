import json, os
def get_current_location():
    return json.load(open(os.path.join(os.path.dirname(__file__), '..', 'config', 'location.json')))