
import random
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils import *

# pour gérer les warnings de certificat SSL
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def generate_customer(dateCreate, retDataCategContact, retDataCategCustomer, enabledModule, testing):
    # on boucle sur les lignes
    url = urlBase + "thirdparties"
    typeTiers = random.choice([0, 1, 2])
    typeFourn = 0
    if createSupplier == 1:
        typeFourn = random.choice([0, 1])

    address, zip, town = get_random_address()
    state_id = get_state_id_from_zip(zip)

    # Codes APE courants
    codes_ape = [
        '6201Z', '6202A', '6202B', '6209Z', '6311Z', '6312Z',
        '4511Z', '4519Z', '4520A', '4520B', '4531Z', '4532Z',
        '4711A', '4711B', '4711C', '4711D', '4719A', '4719B',
        '4321A', '4322A', '4329A', '4331Z', '4332A', '4333Z',
        '5610A', '5610B', '5610C', '5621Z', '5629A', '5629B',
        '6910Z', '6920Z', '7010Z', '7021Z', '7022Z', '7111Z',
        '8559A', '8559B', '8560Z', '8610Z', '8621Z', '8622A',
        '4641Z', '4642Z', '4643Z', '4644Z', '4645Z', '4646Z',
        '2511Z', '2529Z', '2561Z', '2562A', '2562B', '2573A',
        '4910Z', '4920Z', '4941A', '4941B', '4941C', '4942Z',
    ]

    data = {
        "name": fake.company(),
        "address": address,
        "zip": zip,
        "town": town,
        "state_id": state_id,
        "idprof3": random.choice(codes_ape),
        "phone": fake.phone_number(),
        "email": fake.email(),
        # "contact name": df['contact name'][index],
        # "emailcontact": df['emailcontact'][index],
        "client": typeTiers,
        "code_client": "auto",
        "fournisseur": typeFourn,
        "code_fournisseur": "auto",
        "typent_id": random.choice([1, 2, 3, 4]),  # TE_SMALL, TE_GROUP, TE_MEDIUM, TE_ADMIN
        "country_id": random.randint(1, nbCountry),
        "date_creation": dateCreate.strftime('%Y-%m-%d'),
        # "useraffected": df['useraffected'][index],
        # "dateupdate": df['dateupdate'][index],
        # "proprietaire": df['proprietaire'][index],
    }
    r = requests.post(url, headers=headers, json=data, verify=False)
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
        userRandom = get_random_user(fill_users())
        data = { }
        r = requests.post(url + userRandom['id'], headers=headers, json=data, verify=False)
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
        r = requests.post(url, headers=headers, json=data, verify=False)
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
                r = requests.post(url, headers=headers, json=data, verify=False)
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
            r = requests.post(url, headers=headers, json=data, verify=False)
            if r.status_code != 200:
                print("erreur ajout catégorie aléatoire customer ")
    return 1


# Test unitaire
if __name__ == "__main__":
    print(generate_customer(
        dateCreate= fake.date_this_year(),
        retDataCategContact=fill_categories("contact"),
        retDataCategCustomer=fill_categories("customer"),
        enabledModule = get_enabled_modules(),
        testing=True
        ))

# Erreur 1 fois sur 3