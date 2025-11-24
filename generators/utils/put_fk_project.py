import requests
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dolibarr_api import *

from dolibarr_api import *
from generators.generate_utils import *
from generators.utils.get_random_project_id import get_random_project_id
from generators.utils.get_projects_of_contactID import get_projects_of_contactID

def put_fk_project(socID, url, testing=False):
    
    retDataProject = get_projects_of_contactID(socID)
    fk_project = get_random_project_id(retDataProject)
        
    dataProject = {
            "fk_project": fk_project,
            }
    
    r = requests.put(url, headers=headers, json=dataProject)

    if r.status_code != 200:
        if testing:
            print("Erreur lors de l'association du projet :", r.text)

    if testing:
        r = requests.get(url, headers=headers)
        print("Données après mise à jour :", r.text)

# tests unitaires

put_fk_project(574, urlBase + "invoices/481", testing=True)
#put_fk_project(574, urlBase + "orders/1", testing=True)

