from faker import Faker
import random
import string
import requests
import base64
from datetime import timedelta

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from generators.generate_utils import *
from generators.utils.get_random_holiday_type import get_random_holiday_type

fake = Faker('fr_FR')

def generate_holiday(dateCreate, retDataUser, testing=False):

    url = urlBase + "holidays"
    user_id = get_random_user(retDataUser)['id']
    holiday_type = get_random_holiday_type()
    inTime = random.choice([True, False])
    dateDebut = None
    dateFin = None

    if testing:
        print("Type de congé/absence choisi :", holiday_type['id'])
        print("Le congé/absence est-il dans les temps ?", inTime)

    match holiday_type['id']:
        case "1" | "2" : # LEAVE_SICK - LEAVE_OTHER (delais 0)
            dateDebut = dateCreate
            dateFin = fake.date_between(start_date=dateDebut, end_date= dateDebut + timedelta(days=15))
            if testing:
                print("Congé de type sans délai, début :", dateDebut, "fin :", dateFin)
        case "4" : # LEAVE_RTT_FR (delais 7)
            if inTime: # dans les temps
                minDateDebut = dateCreate + timedelta(days=7)
                dateDebut = fake.date_between(start_date=minDateDebut, end_date= minDateDebut + timedelta(days=60))
                dateFin = fake.date_between(start_date=dateDebut, end_date= dateDebut + timedelta(days=10))
                if testing:
                    print("RTT dans les temps, début :", dateDebut,"fin :", dateFin)
            else: # hors délais
                maxDateDebut = dateCreate + timedelta(days=6)
                dateDebut = fake.date_between(start_date=dateCreate, end_date=maxDateDebut)
                dateFin = fake.date_between(start_date=dateDebut, end_date= dateDebut + timedelta(days=10))
                if testing:
                    print("RTT hors délais, début :", dateDebut,"fin :", dateFin)

        case "5" : # LEAVE_PAID_FR (delais 30)
            if inTime: # dans les temps
                minDateDebut = dateCreate + timedelta(days=30)
                dateDebut = fake.date_between(start_date=minDateDebut, end_date= minDateDebut + timedelta(days=180))
                dateFin = fake.date_between(start_date=dateDebut, end_date= dateDebut + timedelta(days=25))
                if testing:
                    print("Congé payé dans les temps, début :", dateDebut,"fin :", dateFin)
            else: # hors délais
                maxDateDebut = dateCreate + timedelta(days=29)
                dateDebut = fake.date_between(start_date=dateCreate, end_date=maxDateDebut)
                dateFin = fake.date_between(start_date=dateDebut, end_date= dateDebut + timedelta(days=25))
                if testing:
                    print("Congé payé hors délais, début :", dateDebut,"fin :", dateFin)
        case _:
            raise ValueError(f"Type de congé {holiday_type['id']} non géré")
    
    if dateDebut is None:
        raise ValueError("dateDebut n'a pas été défini !")

    data ={
        "fk_user": user_id, # id de l'utilisateur
        "date_debut": dateDebut.strftime('%Y-%m-%d'),
        "date_fin": dateFin.strftime('%Y-%m-%d'),
        "fk_type": holiday_type['id'], # id du type de congé/absence
        "halfday": 0,
        "fk_validator": 1, # id du validateur
        "description": fake.sentence(nb_words=6)
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

    
    # update date création (Forbidden)
    """
   url_update = urlBase + "holidays/" + idHoliday
    data_update = {
        "date_create": dateCreate.strftime('%Y-%m-%d'),
        "description": "l'update se fait"
    }
    r_update = requests.put(url_update, headers=headers, json=data_update)
    if r_update.status_code != 200:
        if testing:
            print('Erreur lors de la mise à jour de la date de création du congé/absence', r_update.status_code)
            print (r_update.text)
    else:
        if testing:
            print("Date de création du congé/absence mise à jour avec succès.")
    
    """
    return idHoliday

# Tests
if __name__ == "__main__":
    print("Génération de congés/absences")
    print(generate_holiday(fake.date_this_month(), fill_users(), testing=True))