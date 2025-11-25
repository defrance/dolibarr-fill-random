
import requests
from datetime import datetime, timedelta
from faker import Faker
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from dolibarr_api import *

config = load_config()
fake = Faker('fr_FR')

def fill_projects(limit=100):
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "projects?limit=" + str(limit)
	r = requests.get(url, headers=headers, verify=False)
	if r.status_code != 200:
		print('Erreur lors de la récupération des projets', r.status_code)
		print (r.text)
		exit()

	retDataProjects = r.json()
	
	return retDataProjects

def fill_expensereport_types():
    url = urlBase + "setup/dictionary/expensereport_types"
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code != 200:
        print('Erreur lors de la récupération des types de notes de frais', r.status_code)
        print (r.text)
        exit()
    retDataExpensereportTypes = r.json()
    return retDataExpensereportTypes

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
    print(fill_projects(3))
    print(fill_expensereport_types())
    print(fill_users(3))