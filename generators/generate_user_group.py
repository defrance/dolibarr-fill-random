import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils import *

def generate_user_group(testing = False):
    url = urlBase + "users/groups/"

    if nbNewGroup > 0:

        data={
            "name":fake.company(),
        }

        r = requests.post( url, headers=headers, json=data)

        if r.status_code != 200 :
            print("Erreur lors de la création du groupe d'utilisateur.")
            print(r.status_code)
            print(r.text)
        
        else :
            if testing:
                print("groupe d'utilisateur créé : ")
                print(r.text)

            groupID = r.text
        return groupID

if __name__ == "__main__":
    for  i in range(10):
        print(generate_user_group(testing = True))

