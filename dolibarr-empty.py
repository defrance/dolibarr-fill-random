import string
import requests


from dolibarr_api import *



# on commence par créer les clients et les produits


def delete_customers():
    # on boucle sur les lignes
    url = urlBase + "thirdparties"

    data = {
        "name": fake.company(),
        "address": fake.address(),
        # "zip": df['zip'][index],
        "town": fake.city(),
        "phone": fake.phone_number(),
        # "contact name": df['contact name'][index],
        # "emailcontact": df['emailcontact'][index],
        "client": typeTiers,
        "country_id": random.randint(1, nbCountry),
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
        # "useraffected": df['useraffected'][index],
        # "dateupdate": df['dateupdate'][index],
        # "proprietaire": df['proprietaire'][index],
    }
    #print (data)
    r = requests.post(url, headers=headers, json=data)

    return 1

def delete_socpeoples():
    # on boucle sur les lignes
    url = urlBase + "thirdparties"

    data = {
        "name": fake.company(),
        "address": fake.address(),
        # "zip": df['zip'][index],
        "town": fake.city(),
        "phone": fake.phone_number(),
        # "contact name": df['contact name'][index],
        # "emailcontact": df['emailcontact'][index],
        "client": typeTiers,
        "country_id": random.randint(1, nbCountry),
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
        # "useraffected": df['useraffected'][index],
        # "dateupdate": df['dateupdate'][index],
        # "proprietaire": df['proprietaire'][index],
    }
    #print (data)
    r = requests.post(url, headers=headers, json=data)

    return 1

def delete_warehouses():
    # on boucle sur les lignes
    url = urlBase + "warehouses"
    data = {
        "label": fake.company(),
        "address": fake.address(),
        # "zip": df['zip'][index],
        "town": fake.city(),
        "phone": fake.phone_number(),
        "statut": 1, # actif
        # "contact name": df['contact name'][index],
        # "emailcontact": df['emailcontact'][index],
        "country_id": 1,
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
    }
    #print (data)
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print('Erreur lors de la création du tiers', r.status_code)
        print (r.text)
        return None

    return 1

def delete_products():
    urlProduct = urlBase + "products"

    # on cree le produit
    data = {
        "ref": str(ref),
        "label" :name,
        "tva_tx" : random.choice([5, 10, 20]), # taux de TVA aléatoire entre 5 et 20%
        "type" : random.choice([0, 1]), # produit ou service
        "price" : price,
        "price_min" : price_min,
        "status" : 1, # produit actif
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
        "status_buy" : random.choice([0, 1]),
        "price_base_type" : "HT",
        "price_min_ttc" : 13,
    }

    r = requests.post(urlProduct, headers=headers, json=data)

    return 1

def delete_bills():
    url = urlBase + "invoices"

    data = {
        "type": "0",
        "date" :datefacture.strftime('%Y-%m-%d'),
        "socid": get_random_client(retDataThirdParties),
    }
    r = requests.post(url, headers=headers, json=data)
 
    return 1

def delete_orders():
    url = urlBase + "orders"

    data = {
        "socid": get_random_client(retDataThirdParties),
        "date": dateorder.strftime('%Y-%m-%d'),
    }
    r = requests.post(url, headers=headers, json=data)

    return 1

def delete_proposals():
    url = urlBase + "proposals"

    
    data = {
        "socid": get_random_client(retDataThirdParties),
        "date": dateproposal.strftime('%Y-%m-%d'),
        "duree_validite": 10,
        "fin_validite": date_finvalidite.strftime('%Y-%m-%d'),
        # "duree_validite": random.randint(5, 15),
    }
    r = requests.post(url, headers=headers, json=data)
    return 1

def delete_interventionals():
    url = urlBase + "interventions"

    data = {
        "socid": get_random_client(retDataThirdParties),
        "fk_project": 0,
        "description": fake.catch_phrase(),
        #"date": dateintervention.strftime('%Y-%m-%d'),
    }
    r = requests.post(url, headers=headers, json=data)

    return 1


listfichinters = get_fichinters()
for fichinter in listfichinters:
    intervention = delete_interventionals(fichinter)

listBills = get_bills()
for bill in listBills:
    facture = delete_bills(bill)

listOrders = get_orders()
for order in listOrders:
    commande = delete_orders(order)

listProposals = get_proposals()
for proposal in listProposals:
    propal = delete_proposals(proposal)

listProducts = get_products()
for product in listProducts:
    produit = delete_products(product)

listSocpeoples = get_socpeoples()
for socpople in listSocpeoples:
    contact = delete_socpeoples(socpople)

listCustomers = get_customers()
for customer in listCustomers:
    client = delete_customers(customer)

listWarehouses = get_warehouses()
for warehouse in listWarehouses:
    entrepot = delete_warehouses(warehouse)


