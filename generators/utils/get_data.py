from faker import Faker
import requests
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dolibarr_api import *
from generators.utils.fill_data import *

fake = Faker('fr_FR')


def get_projects_of_contactID(contactID, testing = False):
 url = urlBase +"projects?sortfield=t.rowid&thirdparty_ids=" + str(contactID)
 r = requests.get(url, headers=headers, verify=False)
 if r.status_code != 200:
        if testing:
            print('Erreur lors de la récupération des projets du contactID ' + str(contactID), r.status_code)
            print (r.text)
        return None
 else:
    if testing:
            print('Projets du contactID ' + str(contactID) + ' récupérés avec succès.')
            print( 'nombre de projets: ' + str(len(r.json())) )
            return r.json()
    return r.json()        

def get_random_user_id(retDataUser):
	# on retourne les infos du produit
	return retDataUser[random.randint(1, len(retDataUser)-1)]

def get_random_project_id(retDataProject, testing = False):
	if (len(retDataProject) > 1):
		return retDataProject[random.randint(1, len(retDataProject)-1)]['id']
	elif (len(retDataProject) == 1):
		return retDataProject[0]['id']
	return 0

def get_random_holiday_type(testing=False):
    url = urlBase + "holidays/types?active=1"
    r = requests.get(url, headers=headers, verify=False)

    if r.status_code != 200:
        if testing:
            print('Erreur lors de la récupération des types de congés/absences', r.status_code)
            print(r.text)
        return None

    if testing:
        print("Types de congés/absences récupérés avec succès.")
        

    data = r.json()

    if isinstance(data, dict):
        typesList = list(data.values())
        if testing:
            for t in typesList:
                print("Type ID:", t.get("id"), "Code:", t.get("code"), "delais:" ,t.get("delay"))
    else:
        typesList = data

    if not typesList:
        if testing:
            print("Aucun type de congé trouvé.")
        return None

    randomType = random.choice(typesList)
    

    if testing:
        print("Type aléatoire choisi :", randomType)

    return randomType

def get_random_address():
    fulladdress = fake.address()
    arrayaddress = fulladdress.split("\n")
    arraycpville = arrayaddress[1].split(" ")
    return arrayaddress[0], arraycpville[0], arraycpville[1]


# Test unitaire
if __name__ == "__main__":
    print(get_projects_of_contactID('echec', testing = True)) # id invalide
    print(get_projects_of_contactID(1, testing = True)) # aucun projet 
    print(get_projects_of_contactID(574, testing = True)) # 2 projets TIERS
    print(get_projects_of_contactID(77, testing = True)) # USER /!\ fonctionne pas
    
    retDataUser = fill_users(10)
    print(get_random_user_id(retDataUser))

    print(get_random_project_id(fill_projects(), testing = True)) # a partir de la liste complète
    print(get_random_project_id(get_projects_of_contactID(574), testing = True)) # a partir de la liste d'un contact ayant des projets
    print(get_random_project_id(get_projects_of_contactID(1), testing = True)) # a partir de la liste d'un contact n'ayant pas de projet

    print(get_random_holiday_type(testing=True))
    print(get_random_holiday_type(testing=False))

    adresse, cp, ville = get_random_address()
    print("ville = ", ville)
    print("adresse : ", adresse)
    print("cp :", cp)