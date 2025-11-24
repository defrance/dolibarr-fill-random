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

def generate_order(dateOrder, retDataProduct, retDataThirdParties, retDataWarehouse, retDataUser, testing = False):
    url = urlBase + "orders"
    
    socId = get_random_client(retDataThirdParties)

    if testing:
        socId = 574  # Client de test avec projet

    data = {
        "socid": socId,
        "date": dateOrder.strftime('%Y-%m-%d'),
    }
    r = requests.post(url, headers=headers, json=data)
    orderID = r.text

    urlOrder = url + "/" + str(orderID)
    # on lie un projet du client à la commande

    put_fk_project(socId, urlOrder)

    # on ajoute les lignes
    urlLine = urlOrder + "/lines"
    productRandomList = {}
    for i in range(random.randint(1, 10)):
        # la quantité se trouve en fin de ligne entre parenthèse
        qty = random.randint(1, 10)
        # si il y a un tiret on récupère le produit avant
        # on récupère le produit
        productRandom = get_random_product(retDataProduct)
        # si c'est un produit on le rajoute à la liste pour l'expédition
        # ajoute la ligne de facture
        data = {
            "desc":  productRandom['description'],
            "subprice": productRandom['price'],
            "qty": qty,
            "tva_tx": productRandom['tva_tx'],
            "localtax1_tx": "",
            "localtax2_tx": "",
            "fk_product": productRandom['id'],
            "remise_percent" : 0,
            'info_bits' : 0, 
            "fk_remise_except" : 0, 
            'price_base_type': 'HT',
            "date_start" : "",
            "date_end" : "",
            "product_type" : productRandom['type'],
            "rang": 0, 
            "origin": 0, 
            "origin_id" : "",
            "special_code": 0, 
            "ref_ext": "",
            "pa_ht": 0,
            "fk_parent_line": 0,
            'fk_unit' : 0,
            'fk_fournprice' : 0,
            'pa_ht' : 0,
            'label' : productRandom['type'],
            'multicurrency_subprice' : 0,
            'array_options' : [],
        }
        r = requests.post(urlLine, headers=headers, json=data)
        
        if r.status_code != 200:
            if testing:
                print("Erreur lors de l'ajout de ligne à la commande :", r.text)
        else:
            lineID = r.text


        if productRandom['type'] == "0":
            #  on rajote de la donnée pour l'expédition
            data['entrepot_id'] = get_random_warehouse(retDataWarehouse)
            data['origin_line_id'] = lineID
            data["origin_type"] = 'commande'
            data["detail_batch"] = None
            # on rajoute le produit à la liste pour l'expédition
            productRandomList[productRandom['id']] = data

    if dateOrder.year < yearNow:
        # pour les dates antiérieurs à l'année en cours, on valide la commande
        url = urlBase + "orders/" + str(orderID) + "/validate"
        data = {
            "notrigger": 1,
        }
        r = requests.post(url, headers=headers, json=data)

        url = urlBase + "orders/" + str(orderID) + "/close"
        data = {
            "notrigger": 1,
        }
        r = requests.post(url, headers=headers, json=data)
    else:
        # pour l'année en cours, on ne valide pas toute les commandes
        orderStatut = random.choice([0, 1])
        if orderStatut == 1:
            url = urlOrder + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)  
            # et on ne facture pas toute les commandes
            if random.choice([0, 1]) == 1:
                url = urlOrder + "/setinvoiced"
                data = {
                }
                r = requests.post(url, headers=headers, json=data)  

    # gestion des expéditions si activé et qu'il y a des produits à expédier
    if nb_shipping >0 and len(productRandomList) > 0:
        # print (productRandomList)
        jours_a_ajouter = random.randint(0, 1)
        dateExpedition = dateOrder + timedelta(days=jours_a_ajouter)
        # on ajoute une expédition
        url = urlBase + "shipments"
        data = {
            "socid": socId,
            "date_creation": dateExpedition.strftime('%Y-%m-%d'),
            "date_shipping": dateExpedition.strftime('%Y-%m-%d'),
            "origin_id": orderID,
            "origin_type": 'commande',
            "origin": 'commande',     # pour les versions antérieures à la 22
            "lines": productRandomList
        }
        r = requests.post(url, headers=headers, json=data)
        shippingId = r.text
        if dateOrder.year < yearNow:
            # pour les dates antérieurs à l'année en cours, on valide la commande
            url = urlBase + "shipments/" + str(shippingId) + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)

            url = urlBase + "shipments/" + str(shippingId) + "/close"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)
        else:
            if orderStatut == 1:
                url = urlBase + "shipments/" + str(shippingId) + "/validate"
                data = {
                    "notrigger": 1,
                }
                r = requests.post(url, headers=headers, json=data)  

    # ajout de contact interne ou externe
    if nbOrder_contactInt > 0:
        arrayTypeContactInterne = fill_contact_types("commande", "internal")
        
        if len(arrayTypeContactInterne) >= 1:
            if len(arrayTypeContactInterne) == 1:
                code = arrayTypeContactInterne[0]['code']
            else:
                code = arrayTypeContactInterne[random.randint(1, len(arrayTypeContactInterne)-1)]['code']
            userID = get_random_user(retDataUser)['id']
            url = urlBase + "orders/" + str(orderID) + "/contact/" + userID +"/"+ str(code) + "/internal"
            data = {}
            r = requests.post(url, headers=headers, json=data)

    if nbOrder_contactExt > 0:
        arrayTypeContactExterne = fill_contact_types("commande", "external")
        arrayuser = fill_socpeople(socId)
        if len(arrayuser) > 0:
            if len(arrayuser) == 1:
                userID = arrayuser[0]['id']
            else:
                userID = arrayuser[random.randint(0, len(arrayuser)-1)]['id']
            code = arrayTypeContactExterne[random.randint(1, len(arrayTypeContactExterne)-1)]['code']
            url = urlBase + "orders/" + str(orderID) + "/contact/" + userID +"/"+ str(code) + "/external"
            data = {}
            r = requests.post(url, headers=headers, json=data)
    
    if testing:
        r = requests.get(urlBase + "orders/" + str(orderID), headers=headers)
        print('Commande créée avec succès ID: ' + str(orderID))
        return r.json()
    return 1

if __name__ == "__main__":
    retDataThirdParties = fill_thirdparties("customer")
    retDataThirdParties = fill_thirdparties("supplier")

    print(
        generate_order(
            dateOrder = fake.date_this_year(),
            retDataProduct = fill_products(),
            retDataThirdParties = retDataThirdParties,
            retDataWarehouse= fill_warehouses(),
            retDataUser= fill_users(),
            testing = True
        )
    )