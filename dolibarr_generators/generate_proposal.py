
from faker import Faker
import random
import string
import requests
import base64
import datetime


from dolibarr_api import *
from dolibarr_generators.generate_utils import *


def generate_proposal(dateproposal):
    url = urlBase + "proposals"

    # on rajoute 5 jours à la date de la proposition
    date_finvalidite = dateproposal + timedelta(days=5)  
    dateproposalTs  = dateproposal.timestamp()
    socID = get_random_client(retDataThirdParties)
    data = {
        "socid": socID,
        "date": dateproposalTs,
        "duree_validite": random.randint(5, 15),
    }
    r = requests.post(url, headers=headers, json=data)
    proposalID = r.text

    # on ajoute les lignes attention, pour les propal, il faut utiliser line et pas lines
    urlLine = urlBase + "proposals/" + str(proposalID) + "/line"
    for i in range(random.randint(1, 10)):
        # la quantité se trouve en fin de ligne entre parenthèse
        qty = random.randint(1, 10)
        # si il y a un tiret on récupère le produit avant
        # on récupère le produit
        productRandom = get_random_product(retDataProduct)
        # ajoute la ligne de facture
        data = {
            "fk_product": productRandom['id'],
            "label": productRandom['label'],
            "desc": productRandom['description'],
            "qty": qty,
            "localtax1_tx": "",
            "localtax2_tx": "",
            "remise_percent" : 0,
            'info_bits' : 0, 
            "fk_remise_except" : 0, 
            "product_type" : productRandom['type'],
            "rang": 0, 
            "special_code": 0, 
            "fk_parent_line": 0,
            'fk_fournprice' : 0,
            'pa_ht' : 0,
            "origin": 0, 
            "origin_id" : "",
            "date_start" : "",
            "date_end" : "",
            'multicurrency_subprice' : 0,
            "subprice": productRandom['price'],
            "tva_tx": productRandom['tva_tx'],
            'price_base_type': 'HT',
            'array_options' : [],
            'fk_unit' : 0,
        }
        r = requests.post(urlLine, headers=headers, json=data)


    # si la date est inférieur à l'année en cours
    if date_finvalidite.year < yearNow:
        signed = random.choice([2, 3])
        url = urlBase + "proposals/" + str(proposalID) + "/close"
        data = {
            "status": signed,
        }

        r = requests.post(url, headers=headers, json=data)

        if signed == 2 and date_finvalidite.year == yearNow - 2:
            url = urlBase + "proposals/" + str(proposalID) + "/setinvoiced"
            data = {
            }
            r = requests.post(url, headers=headers, json=data)  
    else:
        if random.choice([0, 1]) == 1:
            url = urlBase + "proposals/" + str(proposalID) + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)  

    # ajout de contact interne ou externe
    if nbProposal_contactInt > 0:
        arrayTypeContactInterne = fill_contact_types("propal", "internal")
        
        if len(arrayTypeContactInterne) >= 1:
            if len(arrayTypeContactInterne) == 1:
                code = arrayTypeContactInterne[0]['code']
            else:
                code = arrayTypeContactInterne[random.randint(1, len(arrayTypeContactInterne)-1)]['code']
            userID = get_random_user(retDataUser)['id']
            url = urlBase + "proposals/" + str(proposalID) + "/contact/" + userID +"/"+ str(code) + "/internal"
            data = {}
            r = requests.post(url, headers=headers, json=data)

    if nbProposal_contactExt > 0:
        arrayTypeContactExterne = fill_contact_types("propal", "external")
        arrayuser = fill_socpeople(socID)
        if len(arrayuser) > 0:
            if len(arrayuser) == 1:
                userID = arrayuser[0]['id']
            else:
                userID = arrayuser[random.randint(0, len(arrayuser)-1)]['id']
            code = arrayTypeContactExterne[random.randint(1, len(arrayTypeContactExterne)-1)]['code']
            url = urlBase + "proposals/" + str(proposalID) + "/contact/" + userID +"/"+ str(code) + "/external"
            data = {}
            r = requests.post(url, headers=headers, json=data)



    return 1