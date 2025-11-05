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

fake = Faker('fr_FR')

def generate_product(dateCreate, retDataWarehouse, retDataCategProduct, enabledModule, testing=False):
    # Référence produit alphanumérique
    ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Nom de produit : combinaison de mot technologique ou marketing
    name = fake.catch_phrase()  # genre "solution intégrée proactive"
    
    price = random.randint(5, 20)  # prix aléatoire entre 5 et 20€
    price_min = price - random.randint(1, 5)  # prix minimum aléatoire entre 1 et 5€ de moins que le prix normal
    status_buy = random.choice([0, 1])  # à l'achat ou non
    # utilisation pour le premier mouvement de stock
    buying_price = price_min - round(price_min * (random.randint(10, 50)/100))  
    # Description plus longue
    description = fake.paragraph(nb_sentences=3)

    urlProduct = urlBase + "products"
    typeProduct = random.choice([0, 1]) # produit ou service
    # on cree le produit
    data = {
        "ref": str(ref),
        "label" :name,
        #faire un get_random_tva a partir de l'api
        "tva_tx" : random.choice([5, 10, 20]), # taux de TVA aléatoire entre 5 et 20%
        "type" : typeProduct,
        "price" : price,
        "price_min" : price_min,
        "status" : 1, # produit actif
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
        "status_buy" : status_buy,
        "price_base_type" : "HT",
        "price_min_ttc" : 13,
    }

    if testing:
        print(urlProduct,headers,data)
    
    r = requests.post(urlProduct, headers=headers, json=data)

    # on récupère l'id du produit crée
    productId = 0
    if r.status_code != 200:
        print('Erreur lors de la création du produit', r.status_code)
        return None
    else:
        productId = r.text


    # on transmet le reste des données par update
    urlProduct = urlBase + "products/" + productId
    data = {
        "description" : description,
    }

    if typeProduct == 1:
        # on rajoute le champ pour les services 
        data["duration_value"] = random.randint(1, 7) #* 3600
        data["duration_unit"] = "h" # heures
    else:
        # on affecte un poids au produit
        data["weight"] = random.randint(1, 10) 
        data["weight_unit"] = "0" # kg


    # en php 8 l'action se fait mais on a une erreur et on ne récupère que l'id modifié
    # le format n'est pas le bon sur l'update, on intercepte l'erreur
    try :
        r = requests.put(urlProduct, headers=headers, json=data)
    except Exception as e:
        # on continue le traitement
        pass

    # sur les produits on rajoute des mouvements de stock
    if typeProduct == 0 and 'stock' in enabledModule:
        # si on a plusieurs entrepots, on ventile le stock sur un autre entrepot
        if len(retDataWarehouse) > 0:
            initWarehouse = get_random_warehouse(retDataWarehouse)
            # ajout de mouvement de stock initial
            urlProduct = urlBase + "stockmovements" 
            data = {
                "product_id" : productId,
                "warehouse_id" : initWarehouse,
                "qty" : random.randint(50, 100) ,
                "type" : 0, # au début on ajoute du stock
                "datem" : dateCreate.strftime('%Y-%m-%d'),
                "movementcode": "INIT-" + productId,
                "movementlabel": "Initial stock",
                "price" : buying_price,
            }
            r = requests.post(urlProduct, headers=headers, json=data)

            # on ventile une partie du stock sur un autre entrepot
            qtyMoved = random.randint(10, 50) ,
            data = {
                "product_id" : productId,
                "warehouse_id" : initWarehouse,
                "qty" : qtyMoved,
                "movementcode": "MOVEOUT-" + productId,
                "movementlabel": "Moving stock out",
                "type" : 1, # au début on enleve du stock
                "datem" : dateCreate.strftime('%Y-%m-%d'),
                "price" : buying_price,
            }
            r = requests.post(urlProduct, headers=headers, json=data)

            # on ventile une partie du stock sur un autre entrepot
            data = {
                "product_id" : productId,
                "warehouse_id" : get_random_warehouse(retDataWarehouse),
                "movementcode": "MOVEIN-" + productId,
                "movementlabel": "Moving stock IN",
                "qty" : qtyMoved,
                "type" : 0, # au début on enleve du stock
                "datem" : dateCreate.strftime('%Y-%m-%d'),
                "price" : buying_price,
            }
            r = requests.post(urlProduct, headers=headers, json=data)


    # gestion des catégories de produit
    if newCategoryProduct > 0 and 'categorie' in enabledModule:
        for i in range(random.randint(0, newCategoryProduct)):
            # on rajoute une catégorie aléatoire
            #categories/5/objects/product/100
            url = urlBase + "categories/" + str(random.choice(retDataCategProduct)['id']) + "/objects/product/" + str(productId)
            data = { }
            r = requests.post(url, headers=headers, json=data)

# ajout alimentation des prix d'achats et des prix de ventes
    # /!\ les prix d'achats sont toujours associés à un fournisseur et une référence fournisseur
    # /!\ les prix peuvent varier en fonction de la quantité

    return 1

# Testing

if __name__ == "__main__":

    print(generate_product(
        dateCreate= fake.date_time_this_year(),
        retDataWarehouse = fill_warehouses(),
        retDataCategProduct = fill_categories("product"),
        enabledModule= get_enabled_modules(),
        testing=False
        

    ))
