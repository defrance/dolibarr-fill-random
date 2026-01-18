import random
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils import *


def generate_intervention(dateIntervention, retDataThirdParties, enabledModule, testing):
    url = urlBase + "interventions"
	# on récupère les contrats associés au client si il y en a
    socId = get_random_client(retDataThirdParties) # 574
    fk_contract = 0
    if 'contrat' in enabledModule:
        retDataContract = fill_contracts(socId)
        fk_contract = get_random_contract(retDataContract)
    fk_project = 0
    if 'project' in enabledModule:
        retDataProject = fill_projects(socId)
        fk_project = get_random_project_id(retDataProject)

    data = {
        "socid": socId,
        "fk_contrat": fk_contract,
        "description": fake.catch_phrase(),
        "fk_project":fk_project
    }
    r = requests.post(url, headers=headers, json=data, verify=False)
    interventionID = r.text

    urlIntervention = url + "/" + str(interventionID)

    # on ajoute les lignes
    urlLine = urlIntervention + "/lines"

    jours_a_ajouter = 0
    for i in range(random.randint(1, 5)):
        jours_a_ajouter += random.randint(0, 1)
        nouvelle_date = dateIntervention + timedelta(days=jours_a_ajouter)
        nouvelle_date += timedelta(hours = random.choice([7, 9, 10, 11,  14, 15, 16]))
        # ajoute la ligne d'intrvention
        data = {
            "description": fake.catch_phrase(),
            "date": nouvelle_date.strftime('%Y-%m-%d %H:%M:%S'),
            "duree": random.randint(1, 4) * 3600, # en secondes  (ancienne version)
            "duration": random.randint(1, 4) * 3600, # en secondes
        }
        r = requests.post(urlLine, headers=headers, json=data, verify=False)
        if testing:
            print ('  Ligne d\'intervention créée ID: ' + r.text)

    # si la date est inférieur à l'année en cours
    if nouvelle_date.year < yearNow:
        url = urlIntervention + "/validate"
        data = {
            "notrigger": 1,
        }
        r = requests.post(url, headers=headers, json=data, verify=False)  

        url = urlIntervention + "/close"
        r = requests.post(url, headers=headers, json={}, verify=False)

        # On met à jour les dates pour les stats
        date_close = nouvelle_date + timedelta(days=jours_a_ajouter)
        data = {
            "datev": nouvelle_date.strftime('%Y-%m-%d %H:%M:%S'),
            "datet": date_close.strftime('%Y-%m-%d %H:%M:%S'),
        }
        r = requests.put(urlIntervention, headers=headers, json=data, verify=False)
    else:
        if random.choice([0, 1]) == 1:
            url = urlIntervention + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data, verify=False)  

            # On met à jour les dates pour les stats
        
            data = {
                "datev": nouvelle_date.strftime('%Y-%m-%d %H:%M:%S'),
            }
            r = requests.put(urlIntervention, headers=headers, json=data, verify=False)

    # On met à jour les dates pour les stats

    data = {
        "datec": dateIntervention.strftime('%Y-%m-%d'),
    }
    r = requests.put(urlIntervention, headers=headers, json=data, verify=False)
    
    if testing:
        r = requests.get(urlIntervention, headers=headers, verify=False)
        print('Intervention créée avec succès ID: ' + str(interventionID))

    return 1

# Test unitaire

if __name__ == "__main__":
    retDataThirdParties = fill_thirdparties("customer")

    print(generate_intervention(
        dateIntervention=fake.date_this_year(),
        retDataThirdParties= retDataThirdParties,
        enabledModule=get_enabled_modules(),
        testing=True
        )
    )
