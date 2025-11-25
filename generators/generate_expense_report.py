from faker import Faker
import random
import string
import requests
import base64
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from generators.utils.fill_data import *
from generators.utils.get_data import *
from generators.utils.put_data import *


def generate_expense_report( dateStart, testing = False):
    url = urlBase + "expensereports"
    userID = get_random_user(fill_users())['id']
    if testing : 
        print("userID : " , userID)
    validatorID = get_random_user(fill_users())['id']


    # Création de la note de frais par défaut en brouillon
    data = {
        "fk_user_author": userID, # par défaut on met l'admin
        "date_debut": dateStart.strftime('%Y-%m-%d'),
        "date_fin": fake.date_between_dates(dateStart, datetime.now()).strftime('%Y-%m-%d'),
        "note_public": fake.text(max_nb_chars=200),
        "note_private": fake.text(max_nb_chars=200),
        "fk_user_validator": validatorID,
    }

    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code != 200:
            print('Erreur lors de la création du note de frais', r.status_code)
            print (r.text)
            return None
        else:
            expenseReportID = r.text
            urlReport = url + "/" + str(expenseReportID)
            if testing :
                print("Note de frais créée avec l'ID : ", expenseReportID)

    except Exception as e:
        print("Erreur lors de la création du note de frais :", e)

    # Ajout des lignes de frais

    projectList = get_projects_of_contactID(userID)
    print(projectList)
    
    """ 
        if len(projectList) = 0 :
        projectList = get_projects_of_contactID(574)
    """

    fkProject = get_random_project_id(projectList)

    dataLine = {
        "comments": fake.text(max_nb_chars=100),
        "fk_project" : fkProject,
        "qty": "1",
        "value_unit": "120.00000000",
        "fk_c_type_fees": 2,
        # vatrate
        "date": "2025-11-02",
        # fk_c_exp_tax_cat,
        #"fk_ecm_files":
        
        }
    
    urlAddLine = urlReport + "/lines"
    
    r = requests.post(urlAddLine, headers=headers, json = dataLine)

    if r.status_code != 200 :
        if testing :  
            print('Erreur lors de la création de la ligne de frais', r.status_code)
            print (r.text)
    else :
        if testing:
            print('création de la ligne de frais.')



    # modification du statut de la note de frais
    # 0 = brouillon
    # 2 = validé en attente d'approbation
    # 5 = approuvé
        # date_approve:
    # 6 = payé
    # 99 = refusé
        # date_refuse:
       # detail_refuse: 
    


# testing

if __name__ == "__main__":
    print(
        generate_expense_report( 
            dateStart= fake.date_this_month(before_today=True), testing = True)
    )

    