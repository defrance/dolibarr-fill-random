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


def generate_customer(dateCreate, retDataUser, retDataCategContact, retDataCategCustomer, enabledModule, testing=False):
    # on boucle sur les lignes
    url = urlBase + "thirdparties"
    typeTiers = random.choice([0, 1, 2])
    typeFourn = 0
    if createSupplier == 1:
        typeFourn = random.choice([0, 1])

    address, zip, town = get_random_address()

    data = {
        "name": fake.company(),
        "address": address,
        "zip": zip,
        "town": town,
        "phone": fake.phone_number(),
        "email": fake.email(),
        # "contact name": df['contact name'][index],
        # "emailcontact": df['emailcontact'][index],
        "client": typeTiers,
        "fournisseur": typeFourn,
        "country_id": random.randint(1, nbCountry),
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
        # "useraffected": df['useraffected'][index],
        # "dateupdate": df['dateupdate'][index],
        # "proprietaire": df['proprietaire'][index],
    }
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print('Erreur lors de la création du tiers', r.status_code)
        print (r.text)
        return None
    else:
        idSoc= r.text

    # ajout de contact
    url = urlBase + "thirdparties/" + idSoc + "/representative/"
    for i in range(random.randint(0, 2)):
        # on rajoute un utilisateur référent 
        userRandom = get_random_user(retDataUser)
        data = { }
        r = requests.post(url + userRandom['id'], headers=headers, json=data)
        if r.status_code != 200:
            print("erreur sur l'ajout d'un utilisateur référent. ")
        
        if testing :
            print("utilisateur référent : ", data)
    
    # ajout de contact
    for i in range(random.randint(0, 3)):
        url = urlBase + "contacts/"
        # on rajoute des contacts externes
        address, zip, town = get_random_address()

        data = {
            "lastname" : fake.last_name(),
            "firstname" : fake.first_name(),
            "socid" : idSoc,
            "address": address,
            "email": fake.email(),
            "zip": zip,
            "town": town,
            "phone": fake.phone_number(),

            "country_id": 1,
        }
        r = requests.post(url, headers=headers, json=data)
        if r.status_code != 200:
            print("erreur sur l'ajout de contact externe. ")
            print (r.text)
            idContact = -1
        else:
            idContact = r.text
         

        # gestion des catégories de contact
        if newCategorySocpeople > 0 and 'categorie' in enabledModule and idContact != -1:
            for i in range(random.randint(0, newCategorySocpeople)):
                # on rajoute une catégorie aléatoire
                url = urlBase + "categories/" + str(random.choice(retDataCategContact)['id']) + "/objects/contact/" + str(idContact)
                data = { }
                r = requests.post(url, headers=headers, json=data)
                if r.status_code != 200:
                    print("erreur ajout catégorie aléatoire Socpeople ")
                    print (r.text)


    # gestion des catégories de tiers
    if newCategoryCustomer > 0 and 'categorie' in enabledModule:
        for i in range(random.randint(0, newCategoryCustomer)):
            # on rajoute une catégorie aléatoire
            #categories/5/objects/product/100
            url = urlBase + "categories/" + str(random.choice(retDataCategCustomer)['id']) + "/objects/customer/" + str(idSoc)
            data = { }
            r = requests.post(url, headers=headers, json=data)
            if r.status_code != 200:
                print("erreur ajout catégorie aléatoire customer ")
    return 1


# Test unitaire
if __name__ == "__main__":
    print(generate_customer(
        dateCreate= fake.date_this_year(),
        retDataUser =fill_users(),
        retDataCategContact=fill_categories("contact"),
        retDataCategCustomer=fill_categories("customer"),
        enabledModule = get_enabled_modules(),
        testing=False
        ))

# Erreur 1 fois sur 3