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

fake = Faker('fr_FR')


def generate_user(dateCreate, testing=False):
    url = urlBase + "users"

    gender = random.choice(['man', 'woman', 'other'])
    lastname = fake.last_name()
    
    if gender == 'man':
        firstname = fake.first_name_male()
    elif gender == 'woman':
        firstname = fake.first_name_female()
    else:
        firstname = fake.first_name()
    login = firstname[0:1]+ '.'+ lastname

    address, zip, town = get_random_address()
    
    data = {
        "login": login,
        "lastname" : lastname,
        "firstname" : firstname,
        'gender' : gender,
        "address": address,
        "zip": zip,
        "town": town,
        "phone": fake.phone_number(),
        "email": firstname.lower() + lastname.lower() + "@" +fake.free_email_domain(),
        "thm": random.randint(20, 80)
    }

    r = requests.post(url, headers=headers, json=data)

    if r.status_code != 200:
        print("Erreur lors de la création de l'utilisateur : ", r.status_code)
        print (r.text)
        return None
    else:
        idSoc= r.text
        if testing:
            r = requests.get(url + '/' + str(idSoc), headers=headers)

    return 1

if __name__ == "__main__":
    print(generate_user(
        dateCreate=fake.date_this_year(),
        testing=False
    ))