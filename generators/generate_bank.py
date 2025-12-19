import random
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils import *

def generate_bank(dateCreate, testing):
    # on boucle sur les lignes
    url = urlBase + "bankaccounts"
    lastname = fake.last_name()
    data = {
        "country_id": 1,
        "ref" : lastname,
        "type" : random.choice([1, 2]), # 0 = epargne, 1, 2 = caisse classique
        "label": fake.company(),
        "rappro" : 0, # pas besoin de rapprocher
        "date_solde" : dateCreate.strftime('%Y-%m-%d'),
        "currency_code" : "EUR",
        'iban_prefix' : fake.iban(),
        "address": fake.address(), 
    }

    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print("Erreur lors de la création de la bank", r.status_code)
        print (r.text)
        return None
    
    if testing:
        print("banque créé : ", data)
    return 1

# Test unitaire
if __name__ == "__main__":
    print(generate_bank(
        dateCreate = fake.date_this_year(),
        testing=True
        ))
