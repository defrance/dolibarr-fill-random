from faker import Faker
import random
import string
import requests
import base64
from datetime import timedelta

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils.get_random_holiday_type import get_random_holiday_type

def generate_holiday(dateCreate, testing=False):

    url = urlBase + "holidays"
    user = get_random_user(fill_users())
    holiday_type = get_random_holiday_type()
    inTime = random.choice([True, False])
    dateDebut = None
    dateFin = None
    status = random.choices(["approve,""cancel","refuse","validate"])

    if testing:
        print("Type de congé/absence choisi :", holiday_type['id'])
        print("Le congé/absence est-il dans les temps ?", inTime)

    match holiday_type['id']:
        case "1" | "2" : # LEAVE_SICK - LEAVE_OTHER (delais 0)
            dateDebut = dateCreate
            dateFin = fake.date_between(start_date = dateDebut, end_date = dateDebut + timedelta(days = 15))
            status = "validate"
            if testing:
                print("Congé de type sans délai, début :", dateDebut, "fin :", dateFin)
        case "4" : # LEAVE_RTT_FR (delais 7)
            if inTime: # dans les temps
                minDateDebut = dateCreate + timedelta(days = 7)
                dateDebut = fake.date_between(start_date = minDateDebut, end_date = minDateDebut + timedelta(days = 60))
                dateFin = fake.date_between(start_date = dateDebut, end_date = dateDebut + timedelta(days = 10))
                if testing:
                    print("RTT dans les temps, début :", dateDebut,"fin :", dateFin)
            else: # hors délais
                maxDateDebut = dateCreate + timedelta(days = 6)
                dateDebut = fake.date_between(start_date = dateCreate, end_date = maxDateDebut)
                dateFin = fake.date_between(start_date = dateDebut, end_date = dateDebut + timedelta(days=10))
                if testing:
                    print("RTT hors délais, début :", dateDebut,"fin :", dateFin)

        case "5" : # LEAVE_PAID_FR (delais 30)
            if inTime: # dans les temps
                minDateDebut = dateCreate + timedelta(days = 30)
                dateDebut = fake.date_between(start_date = minDateDebut, end_date = minDateDebut + timedelta(days = 180))
                dateFin = fake.date_between(start_date = dateDebut, end_date = dateDebut + timedelta(days = 25))
                if testing:
                    print("Congé payé dans les temps, début :", dateDebut,"fin :", dateFin)
            else: # hors délais
                maxDateDebut = dateCreate + timedelta(days = 29)
                dateDebut = fake.date_between(start_date = dateCreate, end_date = maxDateDebut)
                dateFin = fake.date_between(start_date = dateDebut, end_date = dateDebut + timedelta(days = 25))
                if testing:
                    print("Congé payé hors délais, début :", dateDebut,"fin :", dateFin)
        case _:
            raise ValueError(f"Type de congé {holiday_type['id']} non géré")
    
    if dateDebut is None:
        raise ValueError("dateDebut n'a pas été défini !")

    data ={
        "fk_user": user['id'], # id de l'utilisateur
        "date_debut": dateDebut.strftime('%Y-%m-%d'),
        "date_fin": dateFin.strftime('%Y-%m-%d'),
        "fk_type": holiday_type['id'], # id du type de congé/absence
        "halfday": 0,
        "fk_validator": 1, # id du validateur
        "description": fake.sentence(nb_words=6),
        "date_create": dateCreate.strftime('%Y-%m-%d'),
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
        urlHoliday = urlBase + "holidays/" + idHoliday
        r_get = requests.get(urlHoliday, headers = headers)
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
            print("Date de création du congé/absence mise à jour avec succès.")"""
    

    # Acceptation, refus ....

    #user_balance = requests.get(urlHoliday, headers = headers)
    #print("Solde congés/absences de l'utilisateur ID ", user['id'], " : ", user_balance.json().get("solde"))
    
    r = requests.post(urlHoliday + "/" + status[0], headers = headers)
    if r.status_code != 200:
        if testing:
            print(f'Erreur lors du changement de statut du congé/absence en {status[0]}', r.status_code)
            print (r.text)
    else:
        if testing:
            print(f'Statut du congé/absence changé avec succès en {status[0]}.')
    

    if status[0] == "refuse":
        data = {
            "date_refuse": fake.date_between(start_date= dateCreate, end_date = dateDebut).strftime('%Y-%m-%d'),
            "detail_refus": "Raison du refus : " + fake.sentence(nb_words=6)
        }
        r = requests.put(urlHoliday, headers=headers, json=data)
        if r.status_code != 200:
            if testing:
                print('Erreur lors de la mise à jour des détails du congé/absence', r.status_code)
                print (r.text)
        else:
            if testing:
                print("Détails du congé/absence mis à jour avec succès.")
    
    return idHoliday
# Tests
if __name__ == "__main__":
    print("Génération de congés/absences")
    for i in range(5):
        print(generate_holiday(fake.date_this_year(), testing=True))