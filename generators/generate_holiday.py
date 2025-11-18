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
from generators.utils.get_random_holiday_type_id import get_random_holiday_type_id

fake = Faker('fr_FR')

def generate_holiday(dateCreate, retDataUser, testing=False):

    url = urlBase + "holidays"
    user_id = get_random_user(retDataUser)['id']
    holiday_type = get_random_holiday_type_id(testing = testing)
    
    # en fonction du type de congé/absence, prévoir ajustement des dates

    date_debut = fake.date_between(start_date=dateCreate, end_date='+30d')
    date_fin = fake.date_between(start_date=date_debut, end_date='+14d')
    

    data ={
        "fk_user": user_id,
        "date_debut": date_debut.strftime("%Y-%m-%d"),
        "date_fin": date_fin.strftime("%Y-%m-%d"),
        "type": holiday_type,
    }

    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print('Erreur lors de la création du congé/absence', r.status_code)
        print (r.text)
        return None
    else:
        idHoliday= r.text
    if testing :
        print("Congé/absence créé ID : ", idHoliday)
        url_get = urlBase + "holidays/" + idHoliday
        r_get = requests.get(url_get, headers=headers)
        print("Détails : ", r_get.text)
    return idHoliday

# Tests
if __name__ == "__main__":
    print("Génération de congés/absences")
    print(generate_holiday(fake.date_this_month(), fill_users(), testing=True))