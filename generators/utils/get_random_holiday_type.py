import random

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dolibarr_api import *

def get_random_holiday_type(testing=False):
    url = urlBase + "holidays/types?active=1"
    r = requests.get(url, headers=headers, verify=False)

    if r.status_code != 200:
        if testing:
            print('Erreur lors de la récupération des types de congés/absences', r.status_code)
            print(r.text)
        return None

    if testing:
        print("Types de congés/absences récupérés avec succès.")
        

    data = r.json()

    if isinstance(data, dict):
        typesList = list(data.values())
        if testing:
            for t in typesList:
                print("Type ID:", t.get("id"), "Code:", t.get("code"), "delais:" ,t.get("delay"))
    else:
        typesList = data

    if not typesList:
        if testing:
            print("Aucun type de congé trouvé.")
        return None

    randomType = random.choice(typesList)
    

    if testing:
        print("Type aléatoire choisi :", randomType)

    return randomType


# Test unitaire
if __name__ == "__main__":
    print(get_random_holiday_type(testing=True))
    print(get_random_holiday_type(testing=False))

"""
Type ID: 1 Code: LEAVE_SICK delais: 0
Type ID: 2 Code: LEAVE_OTHER delais: 0
Type ID: 4 Code: LEAVE_RTT_FR delais: 7
Type ID: 5 Code: LEAVE_PAID_FR delais: 30
"""
