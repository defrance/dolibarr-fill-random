from faker import Faker
import random
import string
import requests
import base64
import datetime


from dolibarr_api import *

fake = Faker('fr_FR')

# récupération de l'année enccours
yearNow = datetime.now().year

def get_random_address():
    fulladdress = fake.address()
    arrayaddress = fulladdress.split("\n")
    arraycpville = arrayaddress[1].split(" ")
    return arrayaddress[0], arraycpville[0], arraycpville[1]

def generate_user(dateCreate):
    # on boucle sur les lignes
    url = urlBase + "users"
    gender = random.choice(['man', 'woman', 'other'])
    lastname = fake.last_name()
    if gender == 'man':
        firstname = fake.first_name_male()
    elif gender == 'woman':
        firstname = fake.first_name_female()
    else:
        firstname = fake.first_name()
    login = firstname[0:1]+ '.'+ lastname

    address, zip, town = get_random_address()
    data = {
        "login": login,
        "lastname" : lastname,
        "firstname" : firstname,
        'gender' : gender,
        "address": address,
        "zip": zip,
        "town": town,
        "phone": fake.phone_number(),
    }

    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print("Erreur lors de la création de l'utilisateur", r.status_code)
        print (r.text)
        return None
    else:
        idSoc= r.text

    return 1

def generate_bank(dateCreate):
    # on boucle sur les lignes
    url = urlBase + "bankaccounts"
    lastname = fake.last_name()
    data = {
        "country_id": 1,
        "ref" : lastname,
        "type" : random.choice([1, 2]), # 0 = epargne, 1, 2 = caisse classique
        "label": fake.company(),
        "rappro" : 0, # pas besoin de rapprocher
        "date_solde" : dateCreate.strftime('%Y-%m-%d'),
        "currency_code" : "EUR",
        'iban_prefix' : fake.iban(),
        "address": fake.address(),
        
    }
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print("Erreur lors de la création de la bank", r.status_code)
        print (r.text)
        return None

    return 1

def generate_customer(dateCreate):
    # on boucle sur les lignes
    url = urlBase + "thirdparties"
    typeTiers = random.choice([0, 1, 2])
    typeFourn = 0
    if createSupplier == 1:
        typeFourn = random.choice([0, 1])

    address, zip, town = get_random_address()

    data = {
        "name": fake.company(),
        "address": address,
        "zip": zip,
        "town": town,
        "phone": fake.phone_number(),
        "email": fake.email(),
        # "contact name": df['contact name'][index],
        # "emailcontact": df['emailcontact'][index],
        "client": typeTiers,
        "fournisseur": typeFourn,
        "country_id": random.randint(1, nbCountry),
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
        # "useraffected": df['useraffected'][index],
        # "dateupdate": df['dateupdate'][index],
        # "proprietaire": df['proprietaire'][index],
    }
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print('Erreur lors de la création du tiers', r.status_code)
        print (r.text)
        return None
    else:
        idSoc= r.text

    # ajout de contact
    url = urlBase + "thirdparties/" + idSoc + "/representative/"
    for i in range(random.randint(0, 2)):
        # on rajoute un utilisateur référent 
        userRandom = get_random_user(retDataUser)
        data = { }
        r = requests.post(url + userRandom['id'], headers=headers, json=data)

    
    # ajout de contact
    url = urlBase + "contacts/"
    for i in range(random.randint(0, 3)):
        # on rajoute des contacts externes
        address, zip, town = get_random_address()

        data = {
            "lastname" : fake.last_name(),
            "firstname" : fake.first_name(),
            "socid" : idSoc,
            "address": address,
            "email": fake.email(),
            "zip": zip,
            "town": town,
            "phone": fake.phone_number(),

            "country_id": 1,
        }
        r = requests.post(url, headers=headers, json=data)
        idContact = r.text 
        # gestion des catégories de contact
        if newCategorySocpeople > 0:
            for i in range(random.randint(0, newCategorySocpeople)):
                # on rajoute une catégorie aléatoire
                url = urlBase + "categories/" + str(random.choice(retDataCategContact)['id']) + "/objects/contact/" + str(idContact)
                data = { }
                r = requests.post(url, headers=headers, json=data)

    # gestion des catégories de tiers
    if newCategoryCustomer > 0:
        for i in range(random.randint(0, newCategoryCustomer)):
            # on rajoute une catégorie aléatoire
            #categories/5/objects/product/100
            url = urlBase + "categories/" + str(random.choice(retDataCategCustomer)['id']) + "/objects/customer/" + str(idSoc)
            data = { }
            r = requests.post(url, headers=headers, json=data)

    return 1

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

def generate_product(dateCreate):
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
    if typeProduct == 0:
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
    if newCategoryProduct > 0:
        for i in range(random.randint(0, newCategoryProduct)):
            # on rajoute une catégorie aléatoire
            #categories/5/objects/product/100
            url = urlBase + "categories/" + str(random.choice(retDataCategProduct)['id']) + "/objects/product/" + str(productId)
            data = { }
            r = requests.post(url, headers=headers, json=data)

    return 1

def generate_invoices(datefacture):
    url = urlBase + "invoices"

    paye = random.choice([0, 1])
    socId = get_random_client(retDataThirdParties)
    data = {
        "type": "0",
        "date" :datefacture.strftime('%Y-%m-%d'),
        "socid": socId,
    }
    r = requests.post(url, headers=headers, json=data)
    invoiceID = r.text


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

    if datefacture.year < yearNow:
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
                "datepaye" : datefacture.strftime('%Y-%m-%d'),
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

def generate_orders(dateorder):
    url = urlBase + "orders"
    socId = get_random_client(retDataThirdParties)
    data = {
        "socid": socId,
        "date": dateorder.strftime('%Y-%m-%d'),
    }
    r = requests.post(url, headers=headers, json=data)
    orderID = r.text

    # on ajoute les lignes
    urlLine = urlBase + "orders/" + str(orderID) + "/lines"
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
        lineID = r.text

        if productRandom['type'] == "0":
            #  on rajote de la donnée pour l'expédition
            data['entrepot_id'] = get_random_warehouse(retDataWarehouse)
            data['origin_line_id'] = lineID
            data["origin_type"] = 'commande'
            data["detail_batch"] = None
            # on rajoute le produit à la liste pour l'expédition
            productRandomList[productRandom['id']] = data

    if dateorder.year < yearNow:
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
            url = urlBase + "orders/" + str(orderID) + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)  
            # et on ne facture pas toute les commandes
            if random.choice([0, 1]) == 1:
                url = urlBase + "orders/" + str(orderID) + "/setinvoiced"
                data = {
                }
                r = requests.post(url, headers=headers, json=data)  

    # gestion des expéditions si activé et qu'il y a des produits à expédier
    if nb_shipping >0 and len(productRandomList) > 0:
        # print (productRandomList)
        jours_a_ajouter = random.randint(0, 1)
        dateExpedition = dateorder + timedelta(days=jours_a_ajouter)
        # on ajoute une expédition
        url = urlBase + "shipments"
        data = {
            "socid": socId,
            "date_creation": dateExpedition.strftime('%Y-%m-%d'),
            "date_shipping": dateExpedition.strftime('%Y-%m-%d'),
            "origin_id": orderID,
            "origin_type": 'commande',
            "lines": productRandomList
        }
        r = requests.post(url, headers=headers, json=data)
        shippingId = r.text
        if dateorder.year < yearNow:
            # pour les dates antiérieurs à l'année en cours, on valide la commande
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

    return 1

def generate_proposals(dateproposal):
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

def generate_interventionals(dateintervention):
    url = urlBase + "interventions"

	# on récupère les contrats associés au client si il y en a
    socid= get_random_client(retDataThirdParties)
    retDataContract = fill_contracts(socid)
    fk_contract = get_random_contract(retDataContract)

    data = {
        "socid": socid,
        "fk_project": 0,
        "fk_contrat": fk_contract,
        "description": fake.catch_phrase(),
        #"date": dateintervention.strftime('%Y-%m-%d'),
    }
    r = requests.post(url, headers=headers, json=data)
    orderID = r.text

    # on ajoute les lignes
    urlLine = urlBase + "interventions/" + str(orderID) + "/lines"
    jours_a_ajouter = 0
    for i in range(random.randint(1, 5)):
        jours_a_ajouter += random.randint(0, 1)
        nouvelle_date = dateintervention + timedelta(days=jours_a_ajouter)
        nouvelle_date += timedelta(hours = random.choice([7, 9, 10, 11,  14, 15, 16]))
        # ajoute la ligne d'intrvention
        data = {
            "description": fake.catch_phrase(),
            "date": nouvelle_date.strftime('%Y-%m-%d %H:%M:%S'),
            "duree": random.randint(1, 4) * 3600, # en secondes
        }
        r = requests.post(urlLine, headers=headers, json=data)

    # si la date est inférieur à l'année en cours
    if nouvelle_date.year < yearNow:
        url = urlBase + "interventions/" + str(orderID) + "/validate"
        data = {
            "notrigger": 1,
        }
        r = requests.post(url, headers=headers, json=data)  

        url = urlBase + "interventions/" + str(orderID) + "/close"
        r = requests.post(url, headers=headers, json={})

        # On met à jour les dates pour les stats
        url = urlBase + "interventions/" + str(orderID)
        date_close = nouvelle_date + timedelta(days=jours_a_ajouter)
        data = {
            "datev": nouvelle_date.strftime('%Y-%m-%d %H:%M:%S'),
            "datet": date_close.strftime('%Y-%m-%d %H:%M:%S'),
        }
        r = requests.put(url, headers=headers, json=data)
    else:
        if random.choice([0, 1]) == 1:
            url = urlBase + "interventions/" + str(orderID) + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)  

            # On met à jour les dates pour les stats
            url = urlBase + "interventions/" + str(orderID)
            data = {
                "datev": nouvelle_date.strftime('%Y-%m-%d %H:%M:%S'),
            }
            r = requests.put(url, headers=headers, json=data)

    # On met à jour les dates pour les stats
    url = urlBase + "interventions/" + str(orderID)
    data = {
        "datec": dateintervention.strftime('%Y-%m-%d'),
    }
    r = requests.put(url, headers=headers, json=data)


    return 1

def generate_ticket(dateticket):
    # la date doit etre un timestamp
    dateticketTs  =dateticket.timestamp()
    url = urlBase + "tickets"
    # on récupère les contrats associés au client si il y en a
    socid= get_random_client(retDataThirdParties)
    retDataContract = fill_contracts(socid)
    fk_contract = get_random_contract(retDataContract)

    data = {
        "fk_soc": socid,
        'subject': fake.catch_phrase(),
        "fk_contract": fk_contract,
        "message": fake.catch_phrase(),
        "type_code": random.choice(["COM", "HELP", "ISSUE", "PROBLEM", "OTHER", "PROJECT", "REQUEST"]),
        "severity_code": random.choice(["LOW", "NORMAL", "HIGH", "BLOCKING"]),
        "datec": dateticketTs,
    }
    r = requests.post(url, headers=headers, json=data)
    ticketID = r.text


    userAssign = get_random_user(retDataUser)
    # si la date est inférieur à l'année en cours on valide le ticket
    if dateticket.year < yearNow:
        url = urlBase + "tickets/" + str(ticketID)
        date_close = dateticket + timedelta(days=random.randint(1, 5))
        # on affecte un utilisateur au ticket
        status = random.choice([8, 9])
        # on met status et fk_statut pour gérer la retrocompatibilité
        data = {
            "status" : status,
            "fk_statut" : status,
            "resolution" : fake.catch_phrase(),
            "fk_user_assign": userAssign['id'],
            "progress" : 100,
            "date_close" : date_close.strftime('%Y-%m-%d %H:%M:%S'),
        }
        r = requests.put(url, headers=headers, json=data) 
    else:
        status = random.choice([0, 1, 2, 3, 5, 7])
        if status != 0:
            url = urlBase + "tickets/" + str(ticketID)
            date_close = dateticket + timedelta(days=random.randint(1, 5))
            data = {
                "status" : status,
                "fk_statut" : status,
                "progress" : random.randint(0, 100),
                "fk_user_assign": userAssign['id'],
            }
            r = requests.put(url, headers=headers, json=data)

    # gestion des catégories, pas opérationnelle sur les tickets
    # if newCategoryTicket > 0:
    #     for i in range(random.randint(0, newCategoryTicket)):
    #         # on rajoute une catégorie aléatoire
    #         url = urlBase + "categories/" + str(random.choice(retDataCategTicket)['id']) + "/object/ticket/" + str(ticketID)
    #         data = {
    #             "id": random.choice(retDataCategTicket)['id'],
    #         }
    #         r = requests.post(url, headers=headers, json=data)

    return 1

def generate_knowledge(dateknowledge):
    # la date doit etre un timestamp
    dateknowledgeTs  =dateknowledge.timestamp()
        
    url = urlBase + "knowledgemanagement/knowledgerecords"
    data = {
        'question': fake.catch_phrase(),
        "lang": "fr_FR",
        "answer": fake.catch_phrase(),
        "date_creation": dateknowledgeTs,
        "status": 0,
    }
    r = requests.post(url, headers=headers, json=data)
    knowledgeID = r.text
    

    # si la date est inférieur à l'année en cours on valide le ticket
    if dateknowledge.year < yearNow:
        url = urlBase + "knowledgemanagement/" + str(knowledgeID) + "/validate"
        data = {
            "notrigger": 1,
        }
        r = requests.post(url, headers=headers, json=data) 

        status = random.choice([0, 1])
        if status != 0:
            url = urlBase + "knowledgemanagement/" + str(knowledgeID) + "/cancel"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data) 
    else:
        status = random.choice([0, 1])
        if status != 0:
            url = urlBase + "knowledgemanagement/" + str(knowledgeID) + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)  
    return 1

def generate_contracts(datecontract):
    url = urlBase + "contracts"

    data = {
        "socid": get_random_client(retDataThirdParties),
        "date_contrat": datecontract.strftime('%Y-%m-%d'),
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
    if datecontract.year < yearNow :
        r = requests.post(url, headers=headers, json=data)
        # pour les dates antiérieurs à l'année en cours, on valide la commande
        status = "Closed"
    else:
        #pour l'année en cours, on ne valide pas toute les commandes
        if random.choice([0, 1]) == 1:
            r = requests.post(url, headers=headers, json=data)  
            # if datecontract.year < yearNow :
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
            "date_start": datecontract.strftime('%Y-%m-%d'),
            "date_end": datecontract.strftime('%Y-%m-%d'),
            "info_bits": 0,
            "fk_fournprice": 0,
            "pa_ht": 0,
            "array_options": 0,
            "fk_unit": 0,
            "rang": 0,




        }
        r = requests.post(urlLine, headers=headers, json=data)
        lineID = r.text

        datestart = datecontract + timedelta(days=random.randint(1, 30)) 
        datestartTs  =datestart.timestamp()
        dateend = datestart + timedelta(days=random.randint(1, 365)) 
        dateendTs  =dateend.timestamp()
        dateclose = datecontract + timedelta(days=random.randint(1, 365)) 
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
            dateclose = datecontract + timedelta(days=random.randint(1, 365)) 
            data = {
                "notrigger": 1,
                "datestart": datecloseTs,
            }
            r = requests.put(url, headers=headers, json=data)

    return 1

def generate_categories(type):
    # on boucle sur les lignes
    url = urlBase + "categories"
    data = {
        "label": fake.company(),
        "description": fake.catch_phrase(),
        "type": type,
        "status": 1, # actif
    }
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print('Erreur lors de la création de la catégorie', r.status_code)
        print (r.text)
        return None

    return 1


# on mémorise l'heure de début de l'alimentation
start_time = datetime.now()
print("Début de l'alimentation à ", start_time.strftime('%Y-%m-%d %H:%M:%S'))

# creation des catégories
if newCategory > 0:
    for i in range(random.randint(1, newCategory)):
        generate_categories("product")
    for i in range(random.randint(1, newCategory)):
        generate_categories("customer")
    for i in range(random.randint(1, newCategory)):
        generate_categories("contact")
    for i in range(random.randint(1, newCategory)):
        generate_categories("ticket")

retDataCategProduct = fill_categories("product")
retDataCategCustomer = fill_categories("customer")
retDataCategContact = fill_categories("contact")
retDataCategTicket = fill_categories("ticket")

if nbNewWarehouse > 0:
    listWareHouseGen = gen_randow_following_date(yearToFill, nbNewWarehouse, max_interval = dateinterval)
    for dateCreate in listWareHouseGen:
        warehouse = generate_warehouse(dateCreate)

    # on remplit les entrepots et les utilisateurs pour les alimentations aléatoires
    retDataWarehouse = fill_warehouses()

if nbNewUser > 0:
    listUserGen = gen_randow_following_date(yearToFill, nbNewUser, max_interval = dateinterval)
    for dateCreate in listUserGen:
        product = generate_user(dateCreate)

retDataUser = fill_users()

if nbNewBank > 0:
    listBankGen = gen_randow_following_date(yearToFill, nbNewBank, max_interval = dateinterval)
    for dateCreate in listBankGen:
        bank = generate_bank(dateCreate)

retDataBank = fill_banks()
retDataPayment = fill_payement_types()

start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_time
print("Alimentation Initiale : ", duration)
start_prev = datetime.now()

# on cree les clients avant les produits pour associer les prix fournisseurs si besoin
if nbNewClient > 0:
    listClientGen = gen_randow_following_date(yearToFill, nbNewClient, max_interval = dateinterval)
    for dateCreate in listClientGen:
        client = generate_customer(dateCreate)

if nbNewProduct > 0:
    listProductGen = gen_randow_following_date(yearToFill, nbNewProduct, max_interval = dateinterval)
    for dateCreate in listProductGen:
        product = generate_product(dateCreate)


retDataProduct = fill_products()
retDataThirdParties = fill_thirdparties("customer")
if createSupplier == 1:
    retDataFournisseur = fill_thirdparties("supplier")


start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_prev
print("Alimentation Tiers et produits : ", duration)
start_prev = datetime.now()

if nbNewBill > 0:
    listFactureGen = gen_randow_following_date(yearToFill, nbNewBill, max_interval = dateinterval)
    for dateFact in listFactureGen:
        facture = generate_invoices(dateFact)

start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_prev
print("Alimentation Factures et Règlement: ", duration)
start_prev = datetime.now()

if nbNewOrder > 0:
    listOrderGen = gen_randow_following_date(yearToFill, nbNewOrder, max_interval = dateinterval)
    for dateOrder in listOrderGen:
        commande = generate_orders(dateOrder)

start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_prev
print("Alimentation Commande et Expédition : ", duration)
start_prev = datetime.now()

if nbNewProposal > 0:
    listProposalGen = gen_randow_following_date(yearToFill, nbNewProposal, max_interval = dateinterval)
    for dateProposal in listProposalGen:
        propal = generate_proposals(dateProposal)

start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_prev
print("Alimentation Devis : ", duration)
start_prev = datetime.now()

if nbNewContract > 0:
    listContractGen = gen_randow_following_date(yearToFill, nbNewContract, max_interval = dateinterval)
    for dateContract in listContractGen:
        contract = generate_contracts(dateContract)

if nbNewFichinter > 0:
    listInterventionGen = gen_randow_following_date(yearToFill, nbNewFichinter, max_interval = dateinterval)
    for dateInter in listInterventionGen:
        fichinter = generate_interventionals(dateInter)

start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_prev
print("Alimentation Contrat et intervention : ", duration)
start_prev = datetime.now()

if nbNewTicket > 0:
    listTicketGen = gen_randow_following_date(yearToFill, nbNewTicket, max_interval = dateinterval)
    for dateTicket in listTicketGen:
        ticket = generate_ticket(dateTicket)

if nbNewKnowledge > 0:
    listArticleGen = gen_randow_following_date(yearToFill, nbNewKnowledge, max_interval = dateinterval)
    for dateknowledge in listArticleGen:
        ticket = generate_knowledge(dateknowledge)


start_stop = datetime.now()
duration = start_stop - start_prev
print("Alimentation Tickets et articles : ", duration)

print("Fin de l'alimentation à ", start_stop.strftime('%Y-%m-%d %H:%M:%S'))

# on affiche la durée
duration = start_stop - start_time
print("Durée de l'alimentation : ", duration)