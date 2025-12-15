from faker import Faker
import random
import string
import requests
import base64
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

from utils.get_projects_of_contactID import get_projects_of_contactID
from utils.get_random_project_id import get_random_project_id
from utils.get_projects_of_userID import get_projects_of_userID

def generate_expense_report( dateCreate, testing = False):
    url = urlBase + "expensereports"
    dateStart = fake.date_between(start_date=dateCreate, end_date = dateCreate + timedelta(days = 15))
    dateEnd = fake.date_between(start_date=dateStart, end_date = dateStart + timedelta(days = 30))

    user = get_random_user(fill_users())
    userID = user['id']
    if testing : 
        print("userID : " , userID)
    validatorID = user['fk_user'] #par défaut user connecté
    if testing :
        print("validatorID : " , validatorID)


    # Création de la note de frais par défaut en brouillon
    data = {
        "fk_user_author": userID, # par défaut on met l'admin
        "date_debut": dateStart.strftime('%Y-%m-%d'),
        "date_fin": dateEnd.strftime('%Y-%m-%d'),
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
    urlAddLine = urlReport + "/lines"

    projectsList = get_projects_of_userID(userID)

    if not projectsList:
        fkProject = 'null'
    
    elif len(projectsList) > 1 :
            fkProject = projectsList[random.randint(1, len(projectsList)-1)]['element_id']
    
    elif len(projectsList) == 1:
        fkProject = projectsList[0]['element_id']

    if nbExpenseReportLineMax < 1 :
        nbLines = 1
    else :
        nbLines = random.randint(1, nbExpenseReportLineMax)
    
    for i in range (nbLines) :

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
    
        r = requests.post(urlAddLine, headers=headers, json = dataLine)

        if r.status_code != 200 :
            if testing :  
                print('Erreur lors de la création de la ligne de frais', r.status_code)
                print (r.text)
        else :
            if testing:
                print('création de la ligne de frais.')

    status = random.choice(['brouillon','validate', 'approve', 'deny'])

    status = 'approve'  # pour test uniquement
    if testing:
        print("status choisi : " , status)
                
    # validation de la note de frais si elle n'est pas en brouillon
    
    if status != 'brouillon' :

        r = requests.post(urlReport + "/validate", headers=headers)
        if r.status_code != 200 :
            if testing :  
                print('Erreur lors de la validation de la note de frais', r.status_code)
                print (r.text)
        else :
            if testing:
                print('note de frais validée.')

            # probleme API
            dataValidate = {
                'fk_user_valid': validatorID,
                'date_valid': dateCreate.strftime('%Y-%m-%d'),
                'user_create': userID
                }
            
            r = requests.put(urlReport, headers=headers, json = dataValidate)

        # modification user_validate et date_validate

        # refus de la note de frais
        if status == 'deny' :
            data = {
                "details": "Raison du refus : " + fake.sentence(nb_words=6),
            }
            r = requests.post(urlReport + "/" + str(status), headers=headers, json=data)

            if r.status_code != 200 :
                if testing :  
                    print('Erreur lors du changement de statut de la note de frais en :', status, r.status_code)
                    print (r.text)
            else :
                if testing:
                    print('note de frais passée au statut : ' , status)

                # probleme API
                dataDeny = {
                    'date_refuse': dateCreate.strftime('%Y-%m-%d'),
                    'fk_user_refuse': validatorID
                }

                r = requests.put(urlReport, headers=headers, json=dataDeny)

                if r.status_code != 200 : 
                    if testing:
                        print('Erreur lors de la mise à jours du refus.')
                        print(r.text)
                
                if testing:
                    print('data refus update avec succés.')

            
        # approbation de la note de frais
        if status == 'approve' :
            r = requests.post(urlReport + "/" + str(status), headers=headers)
            if r.status_code != 200 :
                if testing :  
                    print('Erreur lors du changement de statut de la note de frais en :', status, r.status_code)
                    print (r.text)
            else :
                if testing:
                    print('note de frais passée au statut : ' , status)

    # paiements

    if status == 'approve':

    
        data_payment = {
"fk_typepayment":2,
"datepaid":"2025-12-15",
"amounts":2,
"bank_account":1
}

        #date_validate}
    # match status :
    #     case "approve":
    #         date_approve = "2025-11-02"
    #         dataStatus = {

    #             "date_approve": date_approve,
    #         }
    #         r = requests.post(urlReport, headers=headers, json=dataStatus)
    #         if r.status_code != 200 :
    #             if testing :  
    #                 print('Erreur lors de la mise à jour de la date d\'approbation de la note de frais', r.status_code)
    #                 print (r.text)
    #         else :
    #             if testing:
    #                 print('date d\'approbation mise à jour.')
    
    # modification du statut de la note de frais
    # 0 = brouillon
    # 2 = validé en attente d'approbation
    # 5 = approuvé
        # date_approve:
    # 6 = payé
    # 99 = refusé
        # date_refuse:
       # detail_refuse: 

# update du validateur de la note de frais après la validation
    """
    validatorID = user['fk_user']
    dataUpdate = {
        "fk_user_validator": validatorID,
    }
    r = requests.put(urlReport, headers=headers, json=dataUpdate)
    if r.status_code != 200 :
        if testing :  
            print('Erreur lors de la mise à jour du validateur de la note de frais', r.status_code)
            print (r.text)
    else :
        if testing:
            print('validateur de la note de frais mis à jour.')
    """

# testing

if __name__ == "__main__":
    for  i in range(10):
        print(
            generate_expense_report( 
                dateCreate= fake.date_this_month(before_today=True), testing = True)
    )

    