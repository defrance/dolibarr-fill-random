import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

def get_enabled_modules():
	# l'url correspond à l'adresse de du site ainsi que le chemin de l'api
	url = urlBase + "setup/modules"
	rEnabledModules = requests.get(url, headers=headers, verify=False)
	if rEnabledModules.status_code != 200:
		print('Erreur lors de la récupération des modules', rEnabledModules.status_code)
		print (rEnabledModules.text)
		exit()

	retDataEnabledModules = rEnabledModules.json()
	return retDataEnabledModules

if __name__ == "__main__":
	print(get_enabled_modules())