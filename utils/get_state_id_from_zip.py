import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import urlBase, headers

# pour gérer les warnings de certificat SSL
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Cache du mapping code département -> state_id
_dept_map = None

def _load_dept_map():
    global _dept_map
    if _dept_map is not None:
        return _dept_map
    r = requests.get(urlBase + 'setup/dictionary/states?country=1&limit=200', headers=headers, verify=False)
    if r.status_code != 200:
        _dept_map = {}
        return _dept_map
    _dept_map = {s['code']: s['id'] for s in r.json()}
    return _dept_map

def get_state_id_from_zip(zip_code):
    """Retourne le state_id Dolibarr à partir d'un code postal français"""
    if not zip_code or len(zip_code) < 2:
        return None
    dept_map = _load_dept_map()
    dept_code = zip_code[:3] if zip_code[:2] == '97' else zip_code[:2]
    return dept_map.get(dept_code)

if __name__ == "__main__":
    for z in ['75001', '69003', '97100', '13001', '00000']:
        print(f'{z} -> state_id={get_state_id_from_zip(z)}')
