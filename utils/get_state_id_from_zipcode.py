import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

# pour gérer les warnings de certificat SSL
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def get_state_id_from_zipcode(zip_code, fk_country=1):
    if fk_country != 1:
        dept_code = zip_code
    else:
        # pour les département français, on bricole un peu
        dept_code = zip_code[:3] if zip_code[:2] == '97' else zip_code[:2]
        
    url = urlBase + "setup/dictionary/states?country=" + str(fk_country) + "&sqlfilters=(t.code_departement:=:" + str(dept_code) + ")&active=1"
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code != 200:
        print('Erreur lors de la récupération des états pour le code postal ' + zip_code, r.status_code)
        print(r.text)
        return None
    data = r.json()
    if not data:
        return '' # si aucun état trouvé, on retourne une chaîne vide (le champ étant optionnel dans Dolibarr)
    #print ('États trouvés pour le code postal ' + zip_code + ':', data)
    return data[0]['id']  # on prend le premier état trouvé (il ne devrait y en avoir qu'un)

if __name__ == "__main__":
    for z in ['75001', '69003', '97100', '13001', '00000']:
        print(f'{z} -> state_id={get_state_id_from_zipcode(z)}')