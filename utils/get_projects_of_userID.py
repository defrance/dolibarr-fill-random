
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

def get_projects_of_userID(id, testing = False):
 url = urlBase + 'users/'+ str(id) +'/elements?elementType=project'

 r = requests.get(url, headers=headers)
 if r.status_code != 200:
        if testing:
            print('Erreur lors de la récupération des projets du contactID ' + str(id), r.status_code)
            print (r.text)
        return None
 else:
    if testing:
            print('Projets du contactID ' + str(id) + ' récupérés avec succès.')

    data = r.json()

    if testing :
         print(data)
    return data


if __name__ == "__main__":
     get_projects_of_userID(7, True)