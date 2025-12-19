import requests
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *


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