from faker import Faker
import random
import string
import requests
import base64
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from generators.generate_utils import *
from generators.utils.put_fk_project import put_fk_project

def generate_invoice(dateFact,retDataPayment, retDataBank, retDataProduct, retDataThirdParties, retDataUser, testing=False):
    url = urlBase + "invoices"


    paye = random.choice([0, 1])
    socId = get_random_client(retDataThirdParties)
    if testing :
        socId = 574  # Client de test avec projet
    data = {
        "type": "0",
        "date" :dateFact.strftime('%Y-%m-%d'),
        "socid": socId,
    }
    r = requests.post(url, headers=headers, json=data)
    invoiceID = r.text
    urlInvoice = url + "/" + str(invoiceID)

     # on lie un projet du client à la commande
    put_fk_project(socId, urlInvoice)

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
        r = requests.post(urlLine, headers=headers, json=data)

    if dateFact.year < yearNow:
        # pour les dates antiérieurs à l'année en cours, on valide la commande
        url = urlBase + "invoices/" + str(invoiceID) + "/validate"
        data = {
            "notrigger": 1,
        }
        r = requests.post(url, headers=headers, json=data)

        # et on réalise le paiement si on a une banque active
        if len(retDataPayment) > 0 and len(retDataBank) > 0:
            if len(retDataPayment) == 1:
                PaymentTypeId = retDataPayment[0]['id']
            else:
                PaymentTypeId = retDataPayment[random.randint(0, len(retDataPayment)-1)]['id']

            url = urlBase + "invoices/" + str(invoiceID) + "/payments"
            data = {
                "datepaye" : dateFact.strftime('%Y-%m-%d'),
                "paymentid" : PaymentTypeId,
                "closepaidinvoices" :  'yes',
                "accountid" : get_random_bank(retDataBank)
            }
            r = requests.post(url, headers=headers, json=data)
    else:
        # pour l'année en cours, on ne valide pas toute les commandes
        if random.choice([0, 1]) == 1:
            url = urlBase + "invoices/" + str(invoiceID) + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)

    # ajout de contact interne ou externe
    if nbInvoice_contactInt > 0:
        arrayTypeContactInterne = fill_contact_types("facture", "internal")
        
        if len(arrayTypeContactInterne) >= 1:
            if len(arrayTypeContactInterne) == 1:
                code = arrayTypeContactInterne[0]['code']
            else:
                code = arrayTypeContactInterne[random.randint(1, len(arrayTypeContactInterne)-1)]['code']
            userID = get_random_user(retDataUser)['id']
            url = urlBase + "orders/" + str(invoiceID) + "/contact/" + userID +"/"+ str(code) + "/internal"
            data = {}
            r = requests.post(url, headers=headers, json=data)

    if nbInvoice_contactExt > 0:
        arrayTypeContactExterne = fill_contact_types("facture", "external")
        arrayuser = fill_socpeople(socId)
        if len(arrayuser) > 0:
            if len(arrayuser) == 1:
                userID = arrayuser[0]['id']
            else:
                userID = arrayuser[random.randint(0, len(arrayuser)-1)]['id']
            code = arrayTypeContactExterne[random.randint(1, len(arrayTypeContactExterne)-1)]['code']
            url = urlBase + "orders/" + str(invoiceID) + "/contact/" + userID +"/"+ str(code) + "/external"
            data = {}
            r = requests.post(url, headers=headers, json=data)
    return 1

# Test unitaire

if __name__ == "__main__":
    retDataThirdParties = fill_thirdparties("customer")
    retDataThirdParties = fill_thirdparties("supplier")

    print(generate_invoice(
        dateFact=fake.date_time_this_year(),
        retDataPayment= fill_payement_types(),
        retDataBank= fill_banks(),
        retDataProduct= fill_products(),
        retDataThirdParties= retDataThirdParties,
        retDataUser= fill_users(),
        testing=True
    ))