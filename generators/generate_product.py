
from datetime import timedelta
import random
import string
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from dolibarr_api import *
from utils import *

def generate_product(dateCreate, retDataWarehouse, retDataCategProduct, enabledModule, testing):
    # Référence produit alphanumérique
    ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Nom de produit : combinaison de mot technologique ou marketing
    name = fake.catch_phrase()  # genre "solution intégrée proactive"
    
    price = random.randint(10, 100)  # prix aléatoire entre 5 et 100€
    price_min = price - random.randint(0,5)  # prix minimum aléatoire entre 1 et 5€ de moins que le prix normal
    status_buy = random.choice([0, 1])  # à l'achat ou non
    

    # utilisation pour le premier mouvement de stock
    buying_price = price_min - round(price_min * (random.randint(10, 50)/100))  
    # Description plus longue
    description = fake.paragraph(nb_sentences=3)

    url = urlBase + "products"

    # recupére les taux de taxes de France par défaut
    
    r = requests.get(urlDictionary + 'vat?actibr=1&fk_country=-1', headers = headers)
    if r.status_code != 200:
        print('erreur lors de la récupération des taux de taxes.')
    vatrateList = r.json()

    try:
        vatrate = vatrateList[random.randint(0, len(vatrateList)-1)]['taux']
        if testing:
                print('taux taxe :', vatrate)
    except:
            print('erreur lors du choix du taux de taxe. Taux pas défaut.')
            vatrate = random.choice([0,5,20])

    typeProduct = random.choice([0, 1]) # produit ou service

    if typeProduct == 0:
        status_batch = 1
    
    else:
        status_batch = None
    
    # on crée le produit
    data = {
        "ref": str(ref),
        "label" :name,
        "tva_tx" : vatrate, # taux de TVA aléatoire entre 5 et 20%
        "type" : typeProduct,
        "price" : price,
        "price_min" : price_min,
        "status" : 1, # produit actif
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
        "status_buy" : status_buy,
        "price_base_type" : "HT",
        "price_min_ttc" : 13,
        "status_batch" : status_batch
    }

    if testing:
        print(url,headers,data)
    
    r = requests.post(url, headers=headers, json=data)

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
            urlStockMovements = urlBase + "stockmovements"
            dlc = None
            dluo = None
            batch = None

            if nbMaxLotByProduct > 0 and 'productbatch' in enabledModule:
                    
                for i in range (random.randint(1, nbMaxLotByProduct)):
                    typeDate = random.choice(['dlc', 'dluo', 'both'])
                    batch = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

                    match typeDate:
                        # 3 a 18 mois (a consommer avant)
                        case 'dlc':
                            dlc = fake.date_between_dates(date_start = dateCreate + timedelta(days=90), date_end = dateCreate + timedelta(days=548) )
        
                        # entre 18 mois et 4 ans (à consommer de préférence avant le :)
                        case 'dluo':
                            dluo = fake.date_between_dates(date_start = dateCreate + timedelta(days = 548), date_end = dateCreate + timedelta (days = 1460))
                        
                        # Si les deux, alors dlc avant dluo
                        case 'both':
                            dlc = fake.date_between_dates(date_start = dateCreate + timedelta(days=90), date_end = dateCreate + timedelta(days=548) )
                            dluo = fake.date_between_dates(date_start = dlc + timedelta(days = 3), date_end = dlc + timedelta (days = 1460)) 

                    data = {
                    "product_id" : productId,
                    "warehouse_id" : initWarehouse,
                    "qty" : random.randint(50, 100) ,
                    "type" : 0, # au début on ajoute du stock
                    "datem" : dateCreate.strftime('%Y-%m-%d'),
                    "movementcode": "INIT-" + productId,
                    "movementlabel": "Initial stock",
                    "price" : buying_price,
                    "batch": batch or None,
                    "eatby": "2020-12-12",# dluo.strftime('%Y-%m-%d') if dluo else None, # API à modifier
                    "sellby": "2020-12-12" # dlc.strftime('%Y-%m-%d') if dlc else None # API à modifier.
                    }

                    r = requests.post(urlStockMovements, headers=headers, json=data)

                    dataUpdateBatch = {
                        
                    }

            else:
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
            
                r = requests.post(urlStockMovements, headers=headers, json=data)

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
            r = requests.post(urlStockMovements, headers=headers, json=data)

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
            r = requests.post(urlStockMovements, headers=headers, json=data)


    # gestion des catégories de produit
    if newCategoryProduct > 0 and 'categorie' in enabledModule:
        for i in range(random.randint(0, newCategoryProduct)):
            # on rajoute une catégorie aléatoire
            #categories/5/objects/product/100
            url = urlBase + "categories/" + str(random.choice(retDataCategProduct)['id']) + "/objects/product/" + str(productId)
            data = { }
            r = requests.post(url, headers=headers, json=data)

    # gestion historique prix de vente
    

    if nbSalePriceHistoryMax > 0 :
        
        for i in range (random.randint(1, nbSalePriceHistoryMax)):
            
            if pourcentageAugPriceMax > 0 :
                pourcentage = random.randint(0, pourcentageAugPriceMax)
                price *= 1 + (pourcentage / 100)
                price = round(price, 2)
                price_min *= 1 + (pourcentage /100)
                price_min = round(price_min,2)

           # par défaut l'augmentation simulée est de 10% 
            else:
                price *= 1.10
                price = round(price, 2)

            dateUpdate = fake.date_between(start_date = dateCreate + timedelta(days = 1), end_date = dateCreate + timedelta (days=30))
            data = {
                "price" : price,
                "price_min" : price_min,
                "date_creation": dateUpdate.strftime('%Y-%m-%d'), # fonctionne pas
                "date_modification": dateUpdate.strftime('%Y-%m-%d') # fonctionne pas
                }
            r = requests.put(urlProduct, headers=headers, json=data)

            if r.status_code != 200:
                if testing : 
                    print ('erreur ajout prix de vente')
                    print(r.status_code)
                    print(r.text)
            else:
                if testing:
                    print('ajout prix historique de vente')
                    print(r.text)


    # gestion des prix d'achats fournisseur

    if status_buy == 1 and nbSupplierProduct >0 :
        supplierList = fill_thirdparties("supplier")

        supplierQty = random.randint(1, nbSupplierProduct)
    
        for i in range (supplierQty) :
            supplierID = get_random_user(supplierList)['id']
            if testing : 
                print(" fournisseur id : ", supplierID)

            if nbSupplierProductPrice > 0 :

                purchasePriceQty = random.randint(1, nbSupplierProductPrice)
                
                qty = random.choice([1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,99,100])
                buyPriceQ = buying_price * qty
                
                for i in range (purchasePriceQty) :

                    dataPurchasePrice = {
                    "qty": qty,
                    "buyprice": buyPriceQ,
                    "price_base_type":"HT",
                    "fourn_id": supplierID,
                    "availability": 1,
                    "ref_fourn": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                    "tva_tx": 20,
                    #"charges": 0,
                    #"remise_percent": 0,
                    #"remise": 0,
                    #"newnpr": 0,
                    #"delivery_time_days": 0,
                    #"supplier_reputation": "string",
                    #"localtaxes_array": [
                    #"string"
                    #],
                    #"newdefaultvatcode": "string",
                    #"multicurrency_buyprice": 0,
                    #"multicurrency_price_base_type": "string",
                    #"multicurrency_tx": 0,
                    #"multicurrency_code": "string",
                    #"desc_fourn": "string",
                    #"barcode": "string",
                    #"fk_barcode_type": 0
            }

                urlPurchasePrice = urlProduct + '/purchase_prices'

                r = requests.post(urlPurchasePrice, headers=headers, json = dataPurchasePrice)

                if r.status_code != 200 : 
                    if testing : 
                        print ('erreur ajout de prix fournisseur')
                        print(r.status_code)
                        print(r.text)
                else:
                    if testing:
                        print('prix fournisseur ajouté : ', buying_price)
                
                if pourcentageAugPriceMax > 0 :
                    pourcentage = random.randint(0, pourcentageAugPriceMax)
                    buying_price *= 1 + (pourcentage / 100)
                    buying_price = round(buying_price,2)
                
                else:
                    buying_price *= 1.10
                    buying_price = round(buying_price,2)

                    if testing:
                        print('nouveau prix fournisseur : ', buying_price)

    return 1

# Testing

if __name__ == "__main__":

    print("début alimentation.")

    for i in range (10):

        print(generate_product(
            dateCreate= fake.date_time_this_year(),
            retDataWarehouse = fill_warehouses(),
            retDataCategProduct = fill_categories("product"),
            enabledModule= get_enabled_modules(),
            testing=True

    ))
        
    print("fin de l'alimentation.")
