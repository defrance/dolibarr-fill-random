import requests
from faker import Faker
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from dolibarr_api import *


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

# Test unitaire
if __name__ == "__main__":
    print(fill_users(3))