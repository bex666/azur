import json, os
CONFIG_FILE=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','config','location.json'))
def get_current_location(): return json.load(open(CONFIG_FILE))
