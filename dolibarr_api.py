import os
import requests
import random
from datetime import datetime, timedelta

#  on récupère le token et le mot de passe du mail
apiToken = open("apitoken.txt", 'r').read()

headers = {
	'DOLAPIKEY': apiToken,
	'DOLAPIENTITY' : '1',				# l'entité de la société (ICI 2)
	'Content-Type': 'application/json', 

	'Accept': 'application/json'
}

### URL du server Dolibarr
urlBase = open("url-dolibarr.txt", 'r').read()


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


def dates_aleatoires_qui_se_suivent(annee, nombre, max_interval=3):
    # Date de départ fixée au 1er janvier de l'année en cours
    # annee_en_cours = datetime.today().year
    date_debut = datetime(annee, 1, 1)

    dates = [date_debut]

    for _ in range(0, nombre):
        # Génère un nombre aléatoire de jours à ajouter (entre 0 et max_interval)
        jours_a_ajouter = random.randint(1, max_interval)
        nouvelle_date = dates[-1] + timedelta(days=jours_a_ajouter)
        dates.append(nouvelle_date)

    return dates

if __name__ == "__main__":
	for _ in range(10):
		print(get_random_product())
		print(get_random_client())
