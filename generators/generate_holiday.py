import random
import requests
from datetime import timedelta
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from dolibarr_api import *
from utils import *

def generate_holiday(dateCreate, testing=False):

    url = urlBase + "holidays"
    user = get_random_user(fill_users())
    holiday_type = get_random_holiday_type()
    inTime = random.choice([True, False])
    dateDebut = None
    dateFin = None
    status = random.choice(["brouillon","approve","cancel","refuse","validate"])
    validatorID = random.choice([1,2,3])

    if testing:
        print("Type de congé/absence choisi :", holiday_type['rowid'])
        print("Le congé/absence est-il dans les temps ?", inTime)
        status = "brouillon"


    match holiday_type['rowid']:
        case "1" | "2" : # LEAVE_SICK - LEAVE_OTHER (delais 0)
            dateDebut = dateCreate
            dateFin = fake.date_between(start_date = dateDebut, end_date = dateDebut + timedelta(days = 15))
            status = "approve"
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
            raise ValueError(f"Type de congé {holiday_type['rowid']} non géré")
    
    if dateDebut is None:
        raise ValueError("dateDebut n'a pas été défini !")

    data ={
        "fk_user": user['id'], # id de l'utilisateur
        "date_debut": dateDebut.strftime('%Y-%m-%d'),
        "date_fin": dateFin.strftime('%Y-%m-%d'),
        "fk_type": holiday_type['rowid'], # id du type de congé/absence
        "halfday": 0,
        "fk_validator": validatorID, # id du validateur
        "description": fake.sentence(nb_words=6),
        #"date_create": dateCreate.strftime('%Y-%m-%d'),
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
    
    if testing :
        print("Détails : ", r_get.text)


    if status == "refuse":

        data = {
            "detail_refuse": "Raison du refus : " + fake.sentence(nb_words=6),
        }
        r = requests.post(urlHoliday + "/" + str(status), headers=headers, json=data)
        if r.status_code != 200:
            if testing:
                print('Erreur lors du refus du congé/absence', r.status_code)
                print (r.text)
        else:
            if testing:
                print("Détails du congé/absence mis à jour avec succès.")

    elif status == "approve":
        r = requests.post(urlHoliday + "/validate", headers = headers)
        if r.status_code != 200:
            if testing:
                print('Erreur lors de la validation du congé/absence approuvé', r.status_code)
                print (r.text)
        else:
            r = requests.post(urlHoliday + "/" + str(status), headers = headers)
            if r.status_code != 200:
                if testing:
                    print('Erreur lors de l\'approbation du congé/absence', r.status_code)
                    print (r.text)
            else:
                if testing:
                    print("Congé/absence approuvé avec succès.")

    else:
        r = requests.post(urlHoliday + "/" + str(status), headers = headers)
        if r.status_code != 200:
            if testing:
                print(f'Erreur lors du changement de statut du congé/absence en {status}', r.status_code)
                print (r.text)
        else:
            if testing:
                print(f'Statut du congé/absence changé avec succès en {status}.')
    
    # update congés/absences utilisateur après acceptation/refus
    
    match status:
        case "refuse":
            data = {
                "date_refuse": fake.date_between(start_date= dateCreate, end_date = dateDebut).strftime('%Y-%m-%d'),
                "date_create": dateCreate.strftime('%Y-%m-%d'),
                "fk_user_refuse": validatorID,
                "fk_user_create": validatorID
            }
        
        case "validate":
            data = {
                "date_valid": fake.date_between(start_date= dateCreate, end_date = dateDebut).strftime('%Y-%m-%d'),
                "fk_user_valid": validatorID,
                "date_create": dateCreate.strftime('%Y-%m-%d'),
                "fk_user_create": validatorID
            }
        
        case "cancel":
            data = {
                "date_cancel": fake.date_between(start_date= dateCreate, end_date = dateDebut).strftime('%Y-%m-%d'),
                "fk_user_cancel": validatorID,
                "date_create": dateCreate.strftime('%Y-%m-%d'),
                "fk_user_create": validatorID
            }

        case "approve":
            dateVal = fake.date_between(start_date= dateCreate, end_date = dateDebut)
            data = {
                "fk_user_valid": validatorID,
                "fk_user_approve": validatorID,
                "date_valid": dateVal.strftime('%Y-%m-%d'),
                "date_approval": fake.date_between(start_date= dateVal, end_date = dateDebut).strftime('%Y-%m-%d'),
                "date_create": dateCreate.strftime('%Y-%m-%d'),
                "fk_user_create": validatorID
            }
    
    r_update = requests.put(urlHoliday, headers=headers, json=data)
    if r_update.status_code != 200:
        if testing:
            print('Erreur lors de la mise à jour du congé/absence après changement de statut', r_update.status_code)
            print (r_update.text)
    else:
        if testing:
            print("Congé/absence mis à jour avec succès après changement de statut.")

    

    
    return idHoliday
# Tests
if __name__ == "__main__":
    print("Génération de congés/absences")
    for i in range(10):
        print(generate_holiday(fake.date_this_year(), testing=True))