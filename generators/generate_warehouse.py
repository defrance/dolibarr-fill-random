from faker import Faker
import random
import string
import requests
import base64
import datetime


from dolibarr_api import *
from generators.generate_utils import *

def generate_warehouse(dateCreate):
    # on boucle sur les lignes
    url = urlBase + "warehouses"
    address, zip, town = get_random_address()
    data = {
        "label": fake.company(),
        "address": address,
        "zip": zip,
        "town": town,
        "phone": fake.phone_number(),
        "statut": 1, # actif
        # "contact name": df['contact name'][index],
        # "emailcontact": df['emailcontact'][index],
        "country_id": 1,
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
    }
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print("Erreur lors de la création de l'entrepot", r.status_code)
        print (r.text)
        return None

    return 1
