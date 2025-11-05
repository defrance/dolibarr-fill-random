import random
import string
import requests
import base64
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from generators.generate_utils import *


def generate_contract(dateContract, retDataThirdParties, retDataProduct, retDataUser, testing=False):
    url = urlBase + "contracts"

    data = {
        "socid": get_random_client(retDataThirdParties),
        "date_contrat": dateContract.strftime('%Y-%m-%d'),
        "commercial_signature_id": get_random_user(retDataUser)['id'],
        "commercial_suivi_id": get_random_user(retDataUser)['id'],
    }

    r = requests.post(url, headers=headers, json=data)
    contractID = r.text
    status = "Draft"
    
    url = urlBase + "contracts/" + str(contractID) + "/validate"
    data = {
        "notrigger": 1,
    }
    if dateContract.year < yearNow :
        r = requests.post(url, headers=headers, json=data)
        # pour les dates antiérieurs à l'année en cours, on valide la commande
        status = "Closed"
    else:
        #pour l'année en cours, on ne valide pas toute les commandes
        if random.choice([0, 1]) == 1:
            r = requests.post(url, headers=headers, json=data)  
            # if dateContract.year < yearNow :
            #     status = "Closed"
            # else:
            status = "Open"

    # on ajoute les lignes de services
    urlLine = urlBase + "contracts/" + str(contractID) + "/lines"
    for i in range(random.randint(1, 3)):
        # la quantité se trouve en fin de ligne entre parenthèse
        qty = random.randint(1, 10)
        # si il y a un tiret on récupère le produit avant
        # on récupère le service
        productRandom = get_random_product(retDataProduct, 1)
        # ajoute la ligne de contract
        # prevoir date start et date fin
        data = {
            "fk_product": productRandom['id'],
            "qty": qty,
            "desc" : fake.catch_phrase(),
            "subprice": productRandom['price'],
            "subprice_excl_tax": productRandom['price'],
            "tva_tx": productRandom['tva_tx'],
            'price_base_type': 'HT',
            "remise_percent":0,
            "localtax1_tx": 0,
            "localtax2_tx": 0,
            "date_start": dateContract.strftime('%Y-%m-%d'),
            "date_end": dateContract.strftime('%Y-%m-%d'),
            "info_bits": 0,
            "fk_fournprice": 0,
            "pa_ht": 0,
            "array_options": 0,
            "fk_unit": 0,
            "rang": 0,

        }
        r = requests.post(urlLine, headers=headers, json=data)
        lineID = r.text

        datestart = dateContract + timedelta(days=random.randint(1, 30)) 
        datestartTs  =datestart.timestamp()
        dateend = datestart + timedelta(days=random.randint(1, 365)) 
        dateendTs  =dateend.timestamp()
        dateclose = dateContract + timedelta(days=random.randint(1, 365)) 
        datecloseTs  =dateclose.timestamp()
        if status == "Open":
            if random.choice([0, 1]) == 1:
                url = urlBase + "contracts/" + str(contractID) + "/lines/" + str(lineID) + "/activate"
                data = {
                    "notrigger": 1,
                    "datestart": datestartTs,
                    "dateend": dateendTs,
                }
                r = requests.put(url, headers=headers, json=data)


        if status == "Closed":
            url = urlBase + "contracts/" + str(contractID) + "/lines/" + str(lineID) + "/activate"
            data = {
                "notrigger": 1,
                "datestart": datestartTs,
                "dateend": dateendTs,
            }
            r = requests.put(url, headers=headers, json=data)

            # on ferme le contrat
            url = urlBase + "contracts/" + str(contractID) + "/lines/" + str(lineID) + "/unactivate"
            dateclose = dateContract + timedelta(days=random.randint(1, 365)) 
            data = {
                "notrigger": 1,
                "datestart": datecloseTs,
            }
            r = requests.put(url, headers=headers, json=data)

    if testing:
        print(data)
    return 1

# Test unitaire

if __name__ == "__main__":
    retDataThirdParties = fill_thirdparties("customer")
    retDataThirdParties = fill_thirdparties("supplier")

    print(
        generate_contract(
        dateContract = fake.date_time_this_year(),
        retDataThirdParties = retDataThirdParties,
        retDataProduct = fill_products(),
        retDataUser = fill_users(),
        testing=False
            )
        )
