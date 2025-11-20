from faker import Faker
import random
import string
import requests
import base64
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from generators.generate_utils import *
from generators.utils.get_projects_of_contactID import get_projects_of_contactID
from generators.utils.get_random_project_id import get_random_project_id


def generate_intervention(dateIntervention, retDataThirdParties, enabledModule, testing=False):
    url = urlBase + "interventions"
	# on récupère les contrats associés au client si il y en a
    socid = get_random_client(retDataThirdParties) #574
    fk_contract = 0
    if 'contrat' in enabledModule:
        retDataContract = fill_contracts(socid)
        fk_contract = get_random_contract(retDataContract)
        retDataProject = get_projects_of_contactID(socid)
        fk_project = get_random_project_id(retDataProject)

    data = {
        "socid": socid,
        "fk_contrat": fk_contract,
        "description": fake.catch_phrase(),
        "fk_project" :  fk_project,
        #"date": dateintervention.strftime('%Y-%m-%d'),
    }
    r = requests.post(url, headers=headers, json=data)
    orderID = r.text

    # on ajoute les lignes
    urlLine = urlBase + "interventions/" + str(orderID) + "/lines"
    jours_a_ajouter = 0
    for i in range(random.randint(1, 5)):
        jours_a_ajouter += random.randint(0, 1)
        nouvelle_date = dateIntervention + timedelta(days=jours_a_ajouter)
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
        "datec": dateIntervention.strftime('%Y-%m-%d'),
    }
    r = requests.put(url, headers=headers, json=data)
    
    if testing:
        urlGet = urlBase + "interventions/" + str(orderID)
        r = requests.get(urlGet, headers=headers)
        print('Intervention créée avec succès ID: ' + str(orderID))
        return r.json()

    return 1

# Test unitaire

if __name__ == "__main__":
    retDataThirdParties = fill_thirdparties("customer")
    retDataThirdParties = fill_thirdparties("supplier")

    print(generate_intervention(
        dateIntervention=fake.date_this_year(),
        retDataThirdParties= retDataThirdParties,
        enabledModule=get_enabled_modules(),
        testing=True
        )
    )
