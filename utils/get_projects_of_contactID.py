
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

def get_projects_of_contactID(contactID, testing = False):
 url = urlBase + 'projects?sortfield=t.rowid&sortorder=ASC&limit=100&thirdparty_ids='+ str(contactID)
 # url = "http://localhost/dolibarr/htdocs/api/index.php/projects?sortfield=t.rowid&sortorder=ASC&limit=100&thirdparty_ids=1"
 r = requests.get(url, headers=headers, verify=False)
 if r.status_code != 200:
        if testing:
            print('Erreur lors de la récupération des projets du contactID ' + str(contactID), r.status_code)
            print (r.text)
        return None
 else:
    if testing:
            print('Projets du contactID ' + str(contactID) + ' récupérés avec succès.')
            print( 'nombre de projets: ' + str(len(r.json())) )
            return r.json()
    return r.json()        


# Test unitaire
if __name__ == "__main__":
    print(get_projects_of_contactID('echec', testing = True)) # id invalide
    print(get_projects_of_contactID(1, testing = True)) # aucun projet 
    print(get_projects_of_contactID(11, testing = True)) # 2 projets TIERS
    print(get_projects_of_contactID(77, testing = True)) # USER /!\ fonctionne pas