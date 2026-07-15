import random
import requests
import sys, os
import datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils import *

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def generate_agendaevent(dateCreate, retDataUser, testing):
    # on boucle sur les lignes
    url = urlBase + "agendaevents"
    userAssign = get_random_user(retDataUser)['id']
    userAssign = random.randint(4, 6) # pour tester on prend un user entre 3 et 5
    
    # on ajoute à la date de début une heure de debut entre 8h et 18h
    dateCreate = datetime(dateCreate.year, dateCreate.month, dateCreate.day, random.randint(8, 18), random.choice([0, 15, 30, 45]), 0)
    datedebut = dateCreate.strftime('%Y-%m-%d %H:%M:%S')

    duree = random.randint(1, 4) * 15 * 60 # durée en minutes 15,30, 45 ou 60 minutes
    datefin = (dateCreate + timedelta(seconds=duree)).strftime('%Y-%m-%d %H:%M:%S')
    data = {
        "country_id": 1,
        "label" : fake.catch_phrase(),
        "type" : 1, # random.choice([1, 2]), # 0 = epargne, 1, 2 = caisse classique
        "rappro" : 0, # pas besoin de rapprocher
        "datep" : datedebut,
        "datef" : datefin,
        "type_code" : random.choice(["AC_TEL", "AC_RDV"]), # random.choice(["AC_TEL", "AC_RDV", "AC_EMAIL", "AC_FAX", "AC_VISIO"]),
        #'note' : fake.catch_phrase(),
        "userownerid": userAssign, 
        "percentage": -1,       # slot ouvert
        "userassigned": userAssign, 
    }

    r = requests.post(url, headers=headers, json=data, verify=False)
    if r.status_code != 200:
        print("Erreur lors de la création de l'évènement", r.status_code)
        print (r.text)
        return None
    
    if testing:
        print("évènement créé : ", data)
    return 1

# Test unitaire
if __name__ == "__main__":
    print(generate_agendaevent(
        dateCreate = fake.date_this_month(after_today=True, before_today=False),
        retDataUser= fill_users(),
        testing=True
        ))
