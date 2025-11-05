import random
import string
import requests
import base64
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from generators.generate_utils import *
hexColor= fake.hex_color()
colorWithoutHash= hexColor.lstrip('#')

def generate_category(type, testing =False):
    # on boucle sur les lignes
    url = urlBase + "categories"
    data = {
        "label": fake.company(),
        "description": fake.catch_phrase(),
        "type": type,
        "status": 1, # actif
        "color": colorWithoutHash,
    }
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print('Erreur lors de la création de la catégorie', r.status_code)
        print (r.text)
        return None
    
    if testing:
        print("Catégorie créée : ", data)

    return 1

# Test unitaire
if __name__ == "__main__":
    print(generate_category(
        type= fake.word(),
        testing= False
    ))
