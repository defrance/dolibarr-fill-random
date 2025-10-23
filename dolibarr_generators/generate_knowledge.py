from faker import Faker
import random
import string
import requests
import base64
import datetime


from dolibarr_api import *
from dolibarr_generators.generate_utils import *

def generate_knowledge(dateknowledge):
    # la date doit etre un timestamp
    dateknowledgeTs  =dateknowledge.timestamp()
        
    url = urlBase + "knowledgemanagement/knowledgerecords"
    data = {
        'question': fake.catch_phrase(),
        "lang": "fr_FR",
        "answer": fake.catch_phrase(),
        "date_creation": dateknowledgeTs,
        "status": 0,
    }
    r = requests.post(url, headers=headers, json=data)
    knowledgeID = r.text
    

    # si la date est inférieur à l'année en cours on valide le ticket
    if dateknowledge.year < yearNow:
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
    return 1