
from faker import Faker
import random
import string
import os
import requests
import base64
import pandas as pd

import pathlib											# utilisation de la bibliothèque pathlib
myFolderpath= pathlib.Path(__file__).parent.resolve()	# on récupère le chemin du programme
os.chdir(myFolderpath)									# on se positionne dans le bon dossier

from dolibarr_api import *

fake = Faker('fr_FR')

# on commence par créer les clients et les produits
nbNewCLient=0
nbNewProduit=0

# puis le reste des données basée sur les clients et produits
nbNewBill=0
nbNewOrder=0
nbNewProposal=0
nbNewFichinter=500
yearToFill=2023
dateinterval = 3

def generate_customer():

    # on boucle sur les lignes
    url = urlBase + "thirdparties"
    typeTiers = random.choice([0, 1, 2])
    data = {
        "name": fake.company(),
        "address": fake.address(),
        # "zip": df['zip'][index],
        "town": fake.city(),
        "phone": fake.phone_number(),
        # "contact name": df['contact name'][index],
        # "emailcontact": df['emailcontact'][index],
        "client": typeTiers,
        "country_id": 1,
        # "useraffected": df['useraffected'][index],
        # "datec": df['datecreated'][index].isoformat(),
        # "dateupdate": df['dateupdate'][index],
        # "proprietaire": df['proprietaire'][index],
    }
    #print (data)
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print('Erreur lors de la création du tiers', r.status_code)
        print (r.text)
        return None
    else:
        idSoc= r.text

    # si il y a une address de facturation
    url = urlBase + "contacts/"


    data = {
        "lastname" : fake.last_name(),
        "firstname" : fake.first_name(),
        "address": fake.address(),
        "phone": fake.phone_number(),

        "country_id": 1,
    }
    r = requests.post(url, headers=headers, json=data)
    #print (r.text)
    
        
    return 1

def generate_product():
    # Référence produit alphanumérique
    ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Nom de produit : combinaison de mot technologique ou marketing
    name = fake.catch_phrase()  # genre "solution intégrée proactive"
    
    price = random.randint(5, 20)  # prix aléatoire entre 5 et 20€
    price_min = price - random.randint(1, 5)  # prix minimum aléatoire entre 1 et 5€ de moins que le prix normal
    # Description plus longue
    description = fake.paragraph(nb_sentences=3)

    urlProduct = urlBase + "products"

    # on ajoute la ligne à la facture
    data = {
        "ref": str(ref),
        "label" :name,
        "tva_tx" : random.choice([5, 10, 20]), # taux de TVA aléatoire entre 5 et 20%
        "type" : random.choice([0, 1]), # produit ou service
        "price" : price,
        "price_min" : price_min,
        "status" : 1, # produit actif
        "status_buy" : random.choice([0, 1]),
        "price_base_type" : "HT",
        "price_min_ttc" : 13,
    }

    r = requests.post(urlProduct, headers=headers, json=data)

    # on récupère l'id du produit crée
    productId = 0
    if r.status_code != 200:
        print('Erreur lors de la création du produit', r.status_code)
        return None
    else:
        productId = r.text
        # print (r.text)


    # on transmet le reste des données par update
    urlProduct = urlBase + "products/" + productId
    data = {
        "description" : description,
    }
    # print (data)
    r = requests.put(urlProduct, headers=headers, json=data)

    return 1

retDataProduct = fill_random_products()

retDataThirdParties = fill_random_thirdparties()

def generate_bills(datefacture):
    url = urlBase + "invoices"

    paye = random.choice([0, 1])

    data = {
        "type": "0",
        "date" :datefacture.strftime('%Y-%m-%d'),
        "socid": get_random_client(retDataThirdParties),
    }
    r = requests.post(url, headers=headers, json=data)
    invoiceID = r.text
    # print ('Facture créée: ', invoiceID)

    # on ajoute les lignes
    urlLine = urlBase + "invoices/" + str(invoiceID) + "/lines"
    for i in range(random.randint(1, 10)):

        # la quantité se trouve en fin de ligne entre parenthèse
        qty = random.randint(1, 10)
        # si il y a un tiret on récupère le produit avant
        # on récupère le produit
        productRandom = get_random_product(retDataProduct)
        # ajoute la ligne de facture
        data = {
            "fk_product": productRandom['id'],
            "qty": qty,
            "subprice": productRandom['price'],
            "tva_tx": productRandom['tva_tx'],
            'price_base_type': 'HT',
        }
        # print (data)
        r = requests.post(urlLine, headers=headers, json=data)

    # on met à jour la facture avec les données supplémentaires
    # url = urlBase + "invoices/" + str(invoiceID)
    # data = {
    #     "date_creation": df['datecreation'][index].isoformat(),
    # }
    # r = requests.put(url, headers=headers, json=data)

    return 1

def generate_orders(dateorder):
    url = urlBase + "orders"

    data = {
        "socid": get_random_client(retDataThirdParties),
        "date": dateorder.strftime('%Y-%m-%d'),
    }
    r = requests.post(url, headers=headers, json=data)
    orderID = r.text
    # print ('Commande créée: ', orderID)

    # on ajoute les lignes
    urlLine = urlBase + "orders/" + str(orderID) + "/lines"
    for i in range(random.randint(1, 10)):

        # la quantité se trouve en fin de ligne entre parenthèse
        qty = random.randint(1, 10)
        # si il y a un tiret on récupère le produit avant
        # on récupère le produit
        productRandom = get_random_product(retDataProduct)
        # ajoute la ligne de facture
        data = {
            "fk_product": productRandom['id'],
            "qty": qty,
            "subprice": productRandom['price'],
            "tva_tx": productRandom['tva_tx'],
            'price_base_type': 'HT',
        }
        # print (data)
        r = requests.post(urlLine, headers=headers, json=data)

    # on met à jour la facture avec les données supplémentaires
    # url = urlBase + "orders/" + str(orderID)
    # data = {
    #     "statut": dateorder.strftime('%Y-%m-%d'),
    # }

    return 1

def generate_proposals(dateproposal):
    url = urlBase + "proposals"

    # on rajoute 5 jours à la date de la proposition
    date_finvalidite = dateproposal + timedelta(days=5)  
    
    data = {
        "socid": get_random_client(retDataThirdParties),
        "date": dateproposal.strftime('%Y-%m-%d'),
        "duree_validite": 10,
        "fin_validite": date_finvalidite.strftime('%Y-%m-%d'),
        # "duree_validite": random.randint(5, 15),
    }
    r = requests.post(url, headers=headers, json=data)
    orderID = r.text
    # print ('Commande créée: ', orderID)

    # on ajoute les lignes attention, pour les propal, il faut utiliser line et pas lines
    urlLine = urlBase + "proposals/" + str(orderID) + "/line"
    for i in range(random.randint(1, 10)):

        # la quantité se trouve en fin de ligne entre parenthèse
        qty = random.randint(1, 10)
        # si il y a un tiret on récupère le produit avant
        # on récupère le produit
        productRandom = get_random_product(retDataProduct)
        # ajoute la ligne de facture
        data = {
            "fk_product": productRandom['id'],
            "qty": qty,
            "subprice": productRandom['price'],
            "tva_tx": productRandom['tva_tx'],
            'price_base_type': 'HT',
        }
        # print (data)
        r = requests.post(urlLine, headers=headers, json=data)
        # print (r.text)

    # on met à jour la facture avec les données supplémentaires
    url = urlBase + "proposals/" + str(orderID)
    data = {
        "duree_validite": 10,
        "fin_validite": date_finvalidite.strftime('%Y-%m-%d'),
    }

    r = requests.put(url, headers=headers, json=data)

    # si la date est inférieur à l'année en cours
    if date_finvalidite.year < 2025:
        signed = random.choice([2, 3])
        url = urlBase + "proposals/" + str(orderID) + "/close"
        data = {
            "status": signed,
        }

        r = requests.post(url, headers=headers, json=data)

        if signed == 2 and date_finvalidite.year == 2023:
            url = urlBase + "proposals/" + str(orderID) + "/setinvoiced"
            data = {
            }
            r = requests.post(url, headers=headers, json=data)  
            # print (r.text)
        # print (r.text)
    else:
        if random.choice([0, 1]) == 1:
            url = urlBase + "proposals/" + str(orderID) + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)  
            #print (r.text)



    # print (r.text)
    return 1

def generate_interventionals(dateintervention):
    url = urlBase + "interventions"

    data = {
        "socid": get_random_client(retDataThirdParties),
        "fk_project": 0,
        "description": fake.catch_phrase(),
        #"date": dateintervention.strftime('%Y-%m-%d'),
    }
    r = requests.post(url, headers=headers, json=data)
    orderID = r.text
    #print ('intervention créée: ', r.text)

    # on ajoute les lignes
    urlLine = urlBase + "interventions/" + str(orderID) + "/lines"
    jours_a_ajouter = 0
    for i in range(random.randint(1, 5)):

        jours_a_ajouter += random.randint(0, 1)
        nouvelle_date = dateintervention + timedelta(days=jours_a_ajouter)
        nouvelle_date += timedelta(hours = random.choice([7, 9, 10, 11,  14, 15, 16]))
        # print (nouvelle_date)
        # ajoute la ligne d'inteventio
        data = {
            "description": fake.catch_phrase(),
            "date": nouvelle_date.strftime('%Y-%m-%d %H:%M:%S'),
            "duree": random.randint(1, 4) * 3600, # en secondes
        }
        r = requests.post(urlLine, headers=headers, json=data)

    # si la date est inférieur à l'année en cours
    if nouvelle_date.year < 2025:
        url = urlBase + "interventions/" + str(orderID) + "/validate"
        data = {
            "notrigger": 1,
        }
        r = requests.post(url, headers=headers, json=data)  

        url = urlBase + "interventions/" + str(orderID) + "/close"
        r = requests.post(url, headers=headers, json={})

    else:
        if random.choice([0, 1]) == 1:
            url = urlBase + "interventions/" + str(orderID) + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)  
            #print (r.text)


    return 1


for _ in range(nbNewProduit):
    produit = generate_product()

for _ in range(nbNewCLient):
    client = generate_customer()


listFactureGen = dates_aleatoires_qui_se_suivent(yearToFill, nbNewBill, max_interval = dateinterval)
for dateFact in listFactureGen:
    facture = generate_bills(dateFact)

listOrderGen = dates_aleatoires_qui_se_suivent(yearToFill, nbNewOrder, max_interval = dateinterval)
for dateOrder in listOrderGen:
    commande = generate_orders(dateOrder)

listProposalGen = dates_aleatoires_qui_se_suivent(yearToFill, nbNewProposal, max_interval = dateinterval)
for dateProposal in listProposalGen:
    propal = generate_proposals(dateProposal)

listInterventionGen = dates_aleatoires_qui_se_suivent(yearToFill, nbNewFichinter, max_interval = dateinterval)
for dateInter in listInterventionGen:
    fichinter = generate_interventionals(dateInter)
