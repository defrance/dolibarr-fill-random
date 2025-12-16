
from faker import Faker
from datetime import timedelta
import random
import string
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *


def generate_productlot (dateCreate, testing):
    url = urlBase + 'productlots/'

    typeDate = random.choice(['dlc', 'dluo'])

    dlc = None
    dluo = None

    match typeDate:
        # 3 a 18 mois
        case 'dlc':
            dlc = fake.date_between_dates(date_start = dateCreate + timedelta(days=90), date_end = dateCreate + timedelta(days=548) )
        # entre 18 mois et 4 ans
        case 'dluo':
            dluo = fake.date_between_dates(date_start = dateCreate + timedelta(days = 548), date_end = dateCreate + timedelta (days = 1460))

# Récupération de la liste des produits
    urlProductsList = urlBase + 'products?sortfield=t.ref&mode=1'
    r = requests.get(urlProductsList, headers=headers)

    if r.status_code != 200:
        print('erreur lors de la récupération de la liste des produits.')
    
    productsList = r.json()

    if len(productsList) > 1 :
            fkProduct = productsList[random.randint(0, len(productsList)-1)]['id']
    
    elif len(productsList) == 1:
            fkProduct = productsList[0]['id']

    data = {
    "fk_product": fkProduct,
    "batch": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
    "eatby": dlc.strftime('%Y-%m-%d') if dlc else None,
    "sellby": dluo.strftime('%Y-%m-%d') if dluo else None
    }

    try:
        r = requests.post(url, headers=headers, json=data)
        if testing:
            print("lot créé.")

    except:
        print("erreur lors de la création du lot")
        print(r.status_code)
        print(r.text)


if __name__ == "__main__":
    for i in range (10):
        generate_productlot(fake.date_this_year(before_today=True),testing = True)