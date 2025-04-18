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

headers = {
	'DOLAPIKEY': apiToken,
	'DOLAPIENTITY' : '1',				# l'entité de la société (ICI 2)
	'Content-Type': 'application/json', 
	'Accept': 'application/json'
}

### URL du server Dolibarr

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
	return retDataWareHouse[random.randint(1, len(retDataWareHouse)-1)]['id']


# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
def fill_random_products():
	url = urlBase + "products?limit=100"
	rRandomProduct = requests.get(url, headers=headers, verify=False)
	if rRandomProduct.status_code != 200:
		print('Erreur lors de la récupération du produit', rRandomProduct.status_code)
		print (rRandomProduct.text)
		exit()

	retDataProduct = rRandomProduct.json()
	return retDataProduct

def get_random_product(retDataProduct):
	# on retourne les infos du produit
	return retDataProduct[random.randint(1, len(retDataProduct)-1)] #['id']

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
