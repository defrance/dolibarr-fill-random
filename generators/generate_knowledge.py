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

def generate_knowledge(dateKnowledge, testing=False):
    # la date doit etre un timestamp
    dateKnowledgeTs  =dateKnowledge.timestamp()
        
    url = urlBase + "knowledgemanagement/knowledgerecords"
    data = {
        'question': fake.catch_phrase(),
        "lang": "fr_FR",
        "answer": fake.catch_phrase(),
        "date_creation": dateKnowledgeTs,
        "status": 0,
    }
    r = requests.post(url, headers=headers, json=data)
    knowledgeID = r.text

    if testing :
        print("Création Knowledge :", data)
        print("ID retourné :", knowledgeID)
    

    # si la date est inférieur à l'année en cours on valide le ticket
    if dateKnowledge.year < yearNow:
        url = urlBase + "knowledgemanagement/" + str(knowledgeID) + "/validate"
        data = {
            "notrigger": 1,
        }
        r = requests.post(url, headers=headers, json=data) 

        status = random.choice([0, 1])
        if status != 0:
            url = urlBase + "knowledgemanagement/" + str(knowledgeID) + "/cancel"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data) 
    else:
        status = random.choice([0, 1])
        if status != 0:
            url = urlBase + "knowledgemanagement/" + str(knowledgeID) + "/validate"
            data = {
                "notrigger": 1,
            }
            r = requests.post(url, headers=headers, json=data)

    if testing :
        print("Statut final :", status)
    return 1

if __name__ == "__main__":
    print(generate_knowledge(
        dateKnowledge=fake.date_time_this_year(),
        testing=False))