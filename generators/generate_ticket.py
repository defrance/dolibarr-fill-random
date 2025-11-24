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
from generators.utils.fill_projects import fill_projects
from generators.utils.put_fk_project import put_fk_project

def generate_ticket(dateTicket, retDataThirdParties, retDataUser, retDataProject, testing = False):
    # la date doit etre un timestamp
    dateTicketTs = dateTicket.timestamp()
    url = urlBase + "tickets"
    # on récupère les contrats associés au client si il y en a
    socid = get_random_client(retDataThirdParties) #574
    retDataContract = fill_contracts(socid)
    fk_contract = get_random_contract(retDataContract)

    data = {
        "fk_soc": socid,
        'subject': fake.catch_phrase(),
        "fk_contract": fk_contract,
        "message": fake.catch_phrase(),
        "type_code": random.choice(["COM", "HELP", "ISSUE", "PROBLEM", "OTHER", "PROJECT", "REQUEST"]),
        "severity_code": random.choice(["LOW", "NORMAL", "HIGH", "BLOCKING"]),
        "datec": dateTicketTs,
    }
    r = requests.post(url, headers=headers, json=data)
    ticketID = r.text

    # on lie un projet du client au ticket
    put_fk_project(socid, urlBase + "tickets/" + str(ticketID))


    userAssign = get_random_user(retDataUser)
    # si la date est inférieur à l'année en cours on valide le ticket
    if dateTicket.year < yearNow:
        url = urlBase + "tickets/" + str(ticketID)
        date_close = dateTicket + timedelta(days=random.randint(1, 5))
        # on affecte un utilisateur au ticket
        status = random.choice([8, 9])
        # on met status et fk_statut pour gérer la retrocompatibilité
        data = {
            "status" : status,
            "fk_statut" : status,
            "resolution" : fake.catch_phrase(),
            "fk_user_assign": userAssign['id'],
            "progress" : 100,
            "date_close" : date_close.strftime('%Y-%m-%d %H:%M:%S'),
        }
        r = requests.put(url, headers=headers, json=data) 
    else:
        status = random.choice([0, 1, 2, 3, 5, 7])
        if status != 0:
            url = urlBase + "tickets/" + str(ticketID)
            date_close = dateTicket + timedelta(days=random.randint(1, 5))
            data = {
                "status" : status,
                "fk_statut" : status,
                "progress" : random.randint(0, 100),
                "fk_user_assign": userAssign['id'],
            }
            r = requests.put(url, headers=headers, json=data)

    # gestion des catégories, pas opérationnelle sur les tickets
    # if newCategoryTicket > 0:
    #     for i in range(random.randint(0, newCategoryTicket)):
    #         # on rajoute une catégorie aléatoire
    #         url = urlBase + "categories/" + str(random.choice(retDataCategTicket)['id']) + "/object/ticket/" + str(ticketID)
    #         data = {
    #             "id": random.choice(retDataCategTicket)['id'],
    #         }
    #         r = requests.post(url, headers=headers, json=data)
    if testing:
        r= requests.get(urlBase + "tickets/" + str(ticketID), headers=headers)
        if r.status_code != 200:
            print("Erreur lors de la récupération du ticket n° " + str(ticketID))
            print("Status code: " + str(r.status_code))
            print("Response: " + r.text)
        
        return r.json()

    return 1

# Testing
if __name__ == "__main__":
    retDataThirdParties = fill_thirdparties("customer")
    retDataThirdParties = fill_thirdparties("supplier")

    print(
        generate_ticket(
            dateTicket = fake.date_time_this_year(),
            retDataThirdParties = retDataThirdParties,
            retDataUser = fill_users(),
            retDataProject= fill_projects(),
            testing = True   
        )
    )