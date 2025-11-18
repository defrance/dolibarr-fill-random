import random

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dolibarr_api import *

def get_random_holiday_type_id(testing = False):
    url = urlBase + "holidays/types?active=1"
    r = requests.get(url, headers=headers, verify=False)

    if r.status_code != 200:
        if testing:
            print('Erreur lors de la récupération des types de congés/absences', r.status_code)
            print (r.text)
        return None
    else:
        if testing:
            print('Types de congés/absences récupérés avec succès.')
        typesList = r.json()
        if len(typesList) == 0:
            if testing:
                print('Aucun type de congé/absence actif trouvé.')
            return None
        randomTypeID = typesList[random.randint(0, len(typesList)-1)]['id']
        if testing:
            print('Type de congé/absence aléatoire sélectionné ID : ', randomTypeID)
        return randomTypeID
    
# Test unitaire
if __name__ == "__main__":
    print(get_random_holiday_type_id(testing = True))