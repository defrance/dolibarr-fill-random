import random
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils import *

def generate_user_group( dateCreate, testing = False):
    url = urlBase + "groups/"

    if nbNewGroup > 0:

        data={
            "groupname":fake.random_name_complements()
        }

        r = requests.post( url, headers=headers, json=data)

        if r.status_code != 200 :
            print("Erreur lors de la création du groupe d'utilisateur.")
            print(r.status_code)
            print(r.text)
        
        else :
            print(r.text)
            groupID = r.text


if __name__ == "__main__":
    for  i in range(50):
        print(generate_user_group())