
import requests
from datetime import datetime, timedelta
from faker import Faker
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from dolibarr_api import *

def fill_groups_users(limit = 100):
    url = urlBase + "users/groups?limit=" + str(limit)
    r = requests.get(url, headers=headers, verify=False)

    if r.status_code != 200:
        print("Erreur lors de la récupération de la liste des groupes d'utilisateurs.")
        print(r.status_code)
        print(r.text)
    
    else :
        retData = r.json()

    return retData

if __name__ == "__main__":
    print(fill_groups_users())