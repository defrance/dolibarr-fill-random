import os
import requests
import random
# import pandas as pd
import yaml
from datetime import datetime, timedelta
#pip install pyyaml


import pathlib											# utilisation de la bibliothèque pathlib
myFolderpath= pathlib.Path(__file__).parent.resolve()	# on récupère le chemin du programme
os.chdir(myFolderpath)									# on se positionne dans le bon dossier

import yaml
def load_config(path='param.yml'):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config()


# on récupère le token et le mot de passe du mail
apiToken = config['connection']['apitoken']
urlBase = config['connection']['urlbase']
dol_version=config['connection']['dol_version']

# on commence par créer les clients et les produits
nbNewUser=config['elements']['new_user']
nbNewClient=config['elements']['new_client']
nbNewProduct=config['elements']['new_product']
nbNewWarehouse=config['elements']['new_warehouse']
nbNewStockMovement=config['elements']['new_stock_movement']
# puis le reste des données basée sur les clients et produits
nbNewBill=config['elements']['new_bill']
nbNewOrder=config['elements']['new_order']
nbNewProposal=config['elements']['new_proposal']
nbNewContract=config['elements']['new_contract']
nbNewFichinter=config['elements']['new_fichinter']
nbNewTicket=config['elements']['new_ticket']
nbNewKnowledge=config['elements']['new_knowledge']

newCategory=config['categories']['new_category']
newCategoryProduct=config['categories']['new_category_product']
newCategoryCustomer=config['categories']['new_category_customer']
newCategorySocpeople=config['categories']['new_category_socpeople']
# newCategoryTicket=config['categories']['new_category_ticket']

# infos lies au projet
nbNewProject=config['project']['new_project']
nbNewTask=config['project']['new_task']
nbNewTaskTime=config['project']['new_task_time']

# autres infos 
yearToFill=config['others']['year_to_fill']
dateinterval = config['others']['date_interval']
nbCountry = config['others']['nb_country']
nb_shipping = config['others']['nb_shipping']

# chargement des contacts
nbProposal_contactInt = config['contacts']['proposal_interne']
nbProposal_contactExt = config['contacts']['proposal_externe']
nbOrder_contactInt = config['contacts']['order_interne']
nbOrder_contactExt = config['contacts']['order_externe']
nbInvoice_contactInt = config['contacts']['invoice_interne']
nbInvoice_contactExt = config['contacts']['invoice_externe']


headers = {
	'DOLAPIKEY': apiToken,
	'DOLAPIENTITY' : '1',				# l'entité de la société (ICI 2)
	'Content-Type': 'application/json', 
	'Accept': 'application/json'
}

# Regles de nommage des fonctions
# fill_ = on récupère les données de l'api et on retourne un tableau
# get_random = on retourne un élément aliéatoire d'un tableau


def fill_users(limit=100):
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "users?limit=" + str(limit)
	rRandomUser = requests.get(url, headers=headers, verify=False)
	if rRandomUser.status_code != 200:
		print('Erreur lors de la récupération des utilisateurs', rRandomUser.status_code)
		print (rRandomUser.text)
		exit()

	retDataUser = rRandomUser.json()
	return retDataUser

def fill_banks():
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "bankaccounts?limit=100"
	rRandomBank = requests.get(url, headers=headers, verify=False)
	if rRandomBank.status_code != 200:
		print('Erreur lors de la récupération des banks', rRandomBank.status_code)
		print (rRandomBank.text)
		exit()

	retDataBank = rRandomBank.json()
	return retDataBank

def get_random_bank(retDataBank):
	if (len(retDataBank) > 1):
		return retDataBank[random.randint(1, len(retDataBank)-1)]['id']
	elif (len(retDataBank) == 1):
		return retDataBank[0]['id']
	return 0

def get_random_user(retDataUser):
	# on retourne les infos du produit
	return retDataUser[random.randint(1, len(retDataUser)-1)]

def fill_contact_types(type, source):
	# type = propal, commande, facture, contrat, fichinter, expedition, ticket,  ...
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "setup/dictionary/contact_types?type=" + type
	url = url + "&sqlfilters=(t.source:=:'" + source + "')"
	rRandomContactType = requests.get(url, headers=headers, verify=False)
	if rRandomContactType.status_code != 200:
		print('Erreur lors de la récupération des contact types', rRandomContactType.status_code)
		print (rRandomContactType.text)
		exit()
	retDataContactType = rRandomContactType.json()
	return retDataContactType

def fill_payement_types():
	url = urlBase + "setup/dictionary/payment_types"
	rRandomPaymentType = requests.get(url, headers=headers, verify=False)
	if rRandomPaymentType.status_code != 200:
		print('Erreur lors de la récupération des payement types', rRandomPaymentType.status_code)
		print (rRandomPaymentType.text)
		exit()
	retDataPayementType = rRandomPaymentType.json()
	return retDataPayementType


def fill_socpeople(socID):
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "contacts?limit=10&thirdparty_ids=" + str(socID)
	rRandomSocPeople = requests.get(url, headers=headers, verify=False)
	if rRandomSocPeople.status_code != 200:
		print('Erreur lors de la récupération des contact ', rRandomSocPeople.status_code)
		print (rRandomSocPeople.text)
		exit()
	retDataSocPeople = rRandomSocPeople.json()
	return retDataSocPeople

def fill_categories(type) :
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "categories?limit=100&type=" + type 
	rRandomCategory = requests.get(url, headers=headers, verify=False)
	if rRandomCategory.status_code != 200:
		print('Erreur lors de la récupération des categories', rRandomCategory.status_code)
		print (rRandomCategory.text)
		exit()
	retDataCategory = rRandomCategory.json()
	return retDataCategory

def fill_warehouses():
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "warehouses?limit=100"
	rRandomWareHouse = requests.get(url, headers=headers, verify=False)
	if rRandomWareHouse.status_code != 200:
		print('Erreur lors de la récupération du produit', rRandomWareHouse.status_code)
		print (rRandomWareHouse.text)
		exit()

	retDataWareHouse = rRandomWareHouse.json()
	return retDataWareHouse

def get_random_warehouse(retDataWareHouse):
	# on retourne les infos du produit
	if (len(retDataWareHouse) > 1):
		return retDataWareHouse[random.	randint(1, len(retDataWareHouse)-1)]['id']
	else:
		return 0

def fill_products():
	url = urlBase + "products?limit=100"
	rRandomProduct = requests.get(url, headers=headers, verify=False)
	if rRandomProduct.status_code != 200:
		print('Erreur lors de la récupération du produit', rRandomProduct.status_code)
		print (rRandomProduct.text)
		exit()

	retDataProduct = rRandomProduct.json()
	return retDataProduct

# all = -1, product = 0, service = 1
def get_random_product(retDataProduct, type = -1):
	if type == -1:
		return retDataProduct[random.randint(1, len(retDataProduct)-1)] 
	# on recherche le bon type de produit
	while True:
		random_product = retDataProduct[random.randint(1, len(retDataProduct)-1)]
		if random_product['type'] == str(type) :
			return random_product

def fill_contracts(socid):
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "contracts?limit=100&thirdparty_ids=" + str(socid)
	url = url + "&sqlfilters=(statut:=:1)"
	rRandomContract = requests.get(url, headers=headers, verify=False)
	if rRandomContract.status_code != 200:
		print('Erreur lors de la récupération du contracts', rRandomContract.status_code)
	retDataContract = rRandomContract.json()
	return retDataContract

def get_random_contract(retDataContract):
	# on retourne les infos du produit
	if (len(retDataContract) > 1):
		return retDataContract[random.randint(0, len(retDataContract)-1)]['id']
	else:
		return 0

def fill_thirdparties():
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "thirdparties?limit=100"
	rRandomClient = requests.get(url, headers=headers, verify=False)
	if rRandomClient.status_code != 200:
		print('Erreur lors de la récupération du produit', rRandomClient.status_code)
	retDataCLient = rRandomClient.json()
	return retDataCLient

def get_random_client(retDataCLient):
	return retDataCLient[random.randint(1, len(retDataCLient)-1)]['id']

def gen_randow_following_date(annee, nombre, max_interval=3):
    # Date de départ fixée au 1er janvier de l'année en cours
    # annee_en_cours = datetime.today().year
    date_debut = datetime(annee, 1, 1)

    dates = [date_debut]

    for _ in range(0, nombre -1):
        # Génère un nombre aléatoire de jours à ajouter (entre 0 et max_interval)
        jours_a_ajouter = random.randint(1, max_interval)
        nouvelle_date = dates[-1] + timedelta(days=jours_a_ajouter)
        dates.append(nouvelle_date)

    return dates

if __name__ == "__main__":
	retDataUser = fill_users()
	retDataProduct = fill_products()
	retDataCLient = fill_thirdparties()
	retDataWareHouse = fill_warehouses()
	for _ in range(2):
		print(get_random_product(retDataProduct))
		print(get_random_client(retDataCLient))
		print(get_random_user(retDataUser))
