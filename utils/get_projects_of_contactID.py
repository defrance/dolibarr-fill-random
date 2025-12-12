
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

def get_projects_of_contactID(contactID, testing = False):
 url = urlBase + 'dolismartprojectsapi/'+ str(contactID) +'/contacts'

 r = requests.get(url, headers=headers, verify=False)
 if r.status_code != 200:
        if testing:
            print('Erreur lors de la récupération des projets du contactID ' + str(contactID), r.status_code)
            print (r.text)
        return None
 else:
    if testing:
            print('Projets du contactID ' + str(contactID) + ' récupérés avec succès.')
    print (str(len(r.json())) + ' projet(s) trouvé(s).') 
    return r.json()  


# Test unitaire
if __name__ == "__main__":
   # print(get_projects_of_contactID('echec', testing = True)) # id invalide
    print(get_projects_of_contactID(1, testing = True)) # aucun projet 
    print(get_projects_of_contactID(11, testing = True)) # 2 projets TIERS
    print(get_projects_of_contactID(77, testing = True)) # USER /!\ fonctionne pas