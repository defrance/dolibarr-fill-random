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


def load_config(path='param.yml'):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config()


#  on récupère le token et le mot de passe du mail
apiToken = config['connection']['apitoken']
urlBase = config['connection']['urlbase']
dol_version=config['connection']['dol_version']

headers = {
	'DOLAPIKEY': apiToken,
	'DOLAPIENTITY' : '1',				# l'entité de la société (ICI 2)
	'Content-Type': 'application/json', 
	'Accept': 'application/json'
}


def fill_random_users():
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "users?limit=100"
	rRandomUser = requests.get(url, headers=headers, verify=False)
	if rRandomUser.status_code != 200:
		print('Erreur lors de la récupération des utilisateurs', rRandomUser.status_code)
		print (rRandomUser.text)
		exit()

	retDataUser = rRandomUser.json()
	return retDataUser

def fill_random_banks():
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "bankaccounts?limit=100"
	rRandomBank = requests.get(url, headers=headers, verify=False)
	if rRandomBank.status_code != 200:
		print('Erreur lors de la récupération des banks', rRandomBank.status_code)
		print (rRandomBank.text)
		exit()

	retDataBank = rRandomBank.json()
	return retDataBank

def get_random_user(retDataUser):
	# on retourne les infos du produit
	return retDataUser[random.randint(1, len(retDataUser)-1)]


def fill_random_categories(type) :
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "categories?limit=100&type=" + type 
	rRandomCategory = requests.get(url, headers=headers, verify=False)
	if rRandomCategory.status_code != 200:
		print('Erreur lors de la récupération des categories', rRandomCategory.status_code)
		print (rRandomCategory.text)
		exit()
	retDataCategory = rRandomCategory.json()
	return retDataCategory

def fill_random_warehouses():
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

def fill_random_products():
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


def fill_random_contracts(socid):
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

def fill_random_thirdparties():
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
	retDataUser = fill_random_users()
	retDataProduct = fill_random_products()
	retDataCLient = fill_random_thirdparties()
	retDataWareHouse = fill_random_warehouses()
	for _ in range(2):
		print(get_random_product(retDataProduct))
		print(get_random_client(retDataCLient))
		print(get_random_user(retDataUser))
