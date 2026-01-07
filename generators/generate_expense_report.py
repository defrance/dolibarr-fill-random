import random
import requests
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils import *

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



    projectsList = get_projects_of_userID(userID)

    if nbExpenseReportLineMax < 1 :
        nbLines = 1
    else :
        nbLines = random.randint(1, nbExpenseReportLineMax)

    # recupére les taux de taxes de France par défaut
    r = requests.get(urlDictionary + 'vat?actibr=1&fk_country=-1', headers = headers)
    if r.status_code != 200:
        print('erreur lors de la récupération des taux de taxes.')
    
    vatrateList = r.json()

    # récupére la liste des types

    r = requests.get(urlDictionary + 'expensereport_types?active=1', headers = headers)
        
    if r.status_code != 200:
        print('erreur lors de la récupération des types de notes de frais.')
    
    typefeesList = r.json()

    # Ajout des lignes de frais
    urlAddLine = urlReport + "/lines"

    for i in range (nbLines) :

        if not projectsList:
            fkProject = 'null'
    
        elif len(projectsList) > 1 :
            fkProject = projectsList[random.randint(0, len(projectsList)-1)]['element_id']
    
        elif len(projectsList) == 1:
            fkProject = projectsList[0]['element_id']

        try:
            typefeeID = typefeesList[random.randint(0, len(typefeesList)-1)]['id']
            if testing:
                print('id type de frais :', typefeeID)
        except:
            print('erreur lors de la récupération de l id du type de frais.')
        
        try:
            vatrate = vatrateList[random.randint(0, len(vatrateList)-1)]['taux']
            if testing:
                print('taux taxe :', vatrate)
        except:
            print('erreur lors du choix du taux de taxe.')

        dataLine = {
            "comments": fake.text(max_nb_chars=100),
            "fk_project" : fkProject,
            "qty": random.randint(1,10),
            "value_unit": random.randint(10,200),
            "fk_c_type_fees": typefeeID,
            "vatrate" : vatrate,
            "date": fake.date_between_dates(dateStart,dateEnd).strftime('%Y-%m-%d'),
        }
    
        r = requests.post(urlAddLine, headers=headers, json = dataLine)

        if r.status_code != 200 :
            if testing :  
                print('Erreur lors de la création de la ligne de frais', r.status_code)
                print (r.text)
        else :
            if testing:
                print('création de la ligne de frais.')

    status = random.choice(['brouillon','validate', 'approve', 'deny', 'cancel', 'paid'])

    
    if testing:
        #status = 'cancel' # 'paid'  'approve'   pour test uniquement
        print("status choisi : " , status)

    # si date de fin pas atteinte, obligatoirement en brouillon

    if dateEnd > datetime.now().date():
        status = 'brouillon'
                
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
            dateValidate = fake.date_between_dates(date_start= dateEnd, date_end= dateEnd + timedelta(days=7))
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
        if status == 'approve' or 'paid' :
            r = requests.post(urlReport + "/approve" , headers=headers)
            if r.status_code != 200 :
                if testing :  
                    print('Erreur lors du changement de statut de la note de frais en :', status, r.status_code)
                    print (r.text)
            else :
                if testing:
                    print('note de frais passée au statut : ' , status)
        
        #annulation de la note de frais
        if status == 'cancel' : 
            data_cancel ={
                'detail': fake.text(max_nb_chars=200)
            }
            r = requests.post(urlReport + "/" + str(status), headers=headers, json = data_cancel)
            if r.status_code != 200 :
                if testing :  
                    print('Erreur lors du changement de statut de la note de frais en :', status, r.status_code)
                    print (r.text)
            else :
                if testing:
                    print('note de frais passée au statut : ' , status)

    # paiements des notes approuvées

    if status == 'paid':

        r = requests.get( urlDictionary + 'payment_types?active=1', headers=headers)

        if r.status_code != 200:
            print('erreur lors de la récupération des types de paiements.')
            print(r.status_code)
            print(r.text)

        
        paymentTypeList = r.json()

        try:
          fkTypePayment = paymentTypeList[random.randint(0, len(paymentTypeList)-1)]['id']
          if testing:
            print('id type de paiement :', fkTypePayment)
        except:
            print('erreur lors du choix du types de paiement.')
    
    # Prévoir récupération du total de la note de frais.

        data_payment = {
            "fk_typepayment":fkTypePayment,
            "datepaid":dateValidate.strftime('%Y-%m-%d'),
            "amounts":200,
            "bank_account":3
        }
        r = requests.post(urlReport + "/payments", headers = headers, json = data_payment)

        if r.status_code != 200:
            print('erreur lors du paiement de la note de frais.')
            print(r.status_code)
            print(r.text)

# testing

if __name__ == "__main__":
    for  i in range(5):
        print(
            generate_expense_report( 
                dateCreate= fake.date_this_year(before_today=True), testing = True)
    )

    