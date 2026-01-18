import random
import requests
import calendar
from datetime import datetime, timedelta, date
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils import *


def generate_expense_report(dateCreate, testing=False):
    url = urlBase + "expensereports"
    urlConf = urlBase + "setup/conf/EXPENSEREPORT_PREFILL_DATES_WITH_CURRENT_MONTH"


    # CONFIG : PREFILL MONTHLY

    try:
        r = requests.get(urlConf, headers=headers, verify=False)

        if r.status_code != 200:
            configPrefillActived = "0"
        else:
            raw = r.text.strip()
            configPrefillActived = raw.strip('"').strip()

        if testing:
            print("Config monthly raw:", repr(r.text))
            print("Config monthly parsed :", configPrefillActived)

    except Exception as e:
        print("Erreur récupération config monthly :", e)
        configPrefillActived = "0"


    # DATES NOTE DE FRAIS

    if configPrefillActived == "1":
        dateStart = dateCreate.replace(day=1)
        last_day = calendar.monthrange(dateCreate.year, dateCreate.month)[1]
        dateEnd = dateCreate.replace(day=last_day)

        if testing:
            print("Monthly ACTIVÉ")
    else:
        dateStart = fake.date_between(
            start_date=dateCreate,
            end_date=dateCreate + timedelta(days=15)
        )
        dateEnd = fake.date_between(
            start_date=dateStart,
            end_date=dateStart + timedelta(days=30)
        )

        if testing:
            print("Monthly DÉSACTIVÉ (random)")

    if testing:
        print("dateStart :", dateStart)
        print("dateEnd   :", dateEnd)


    # UTILISATEUR

    user = get_random_user(fill_users())
    userID = user["id"]
    validatorID = user["fk_user"]

    if testing:
        print("userID :", userID)
        print("validatorID :", validatorID)


    # CRÉATION NOTE DE FRAIS (BROUILLON)

    data = {
        "fk_user_author": userID,
        "date_debut": dateStart.strftime("%Y-%m-%d"),
        "date_fin": dateEnd.strftime("%Y-%m-%d"),
        "note_public": fake.text(max_nb_chars=200),
        "note_private": fake.text(max_nb_chars=200),
        "fk_user_validator": validatorID,
    }

    r = requests.post(url, headers=headers, json=data, verify=False)
    if r.status_code != 200:
        print("Erreur création note de frais", r.status_code)
        print(r.text)
        return None

    expenseReportID = r.text
    urlReport = f"{url}/{expenseReportID}"

    if testing:
        print("Note de frais créée ID :", expenseReportID)


    # LIGNES DE FRAIS

    projectsList = get_projects_of_userID(userID)

    maxLines = max(1, nbExpenseReportLineMax)
    nbLines = random.randint(1, maxLines)

    r = requests.get(urlDictionary + "vat?actibr=1&fk_country=-1", headers=headers, verify=False)
    vatrateList = r.json()

    r = requests.get(urlDictionary + "expensereport_types?active=1", headers=headers, verify=False)
    typefeesList = r.json()

    totalAmountHT = 0
    for _ in range(nbLines):
        if not projectsList:
            fkProject = None
        else:
            fkProject = random.choice(projectsList)["element_id"]

        typefee = random.choice(typefeesList)
        typefeeID = typefee["id"]
        typefeeCode = typefee["code"]
        vatrate = random.choice(vatrateList)["taux"]
        
        qty, value_unit = get_realistic_qty_price(typefeeCode)

        if testing:
            print(f"Type frais {typefeeCode} → qty = {qty}, value_unit = {value_unit} €")

        totalAmountHT += value_unit * qty
        dataLine = {
            "comments": fake.text(max_nb_chars=100),
            "fk_project": fkProject,
            "qty": qty,
            "value_unit": value_unit,
            "fk_c_type_fees": typefeeID,
            "vatrate": vatrate,
            "date": fake.date_between_dates(dateStart, dateEnd).strftime("%Y-%m-%d"),
        }

        r = requests.post(urlReport + "/line", headers=headers, json=dataLine, verify=False)
        if testing and r.status_code == 200:
            print("Ligne de frais ajoutée")

    
    # STATUT

    status = random.choice(["brouillon", "validate", "approve", "deny", "cancel", "paid"])

    if testing:
        print("Status initial :", status)

    if dateEnd > datetime.now().date():
        status = 'brouillon'
                
    # validation de la note de frais si elle n'est pas en brouillon
    if status != 'brouillon' :
        r = requests.post(urlReport + "/validate", headers=headers, verify=False)
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
            
            r = requests.put(urlReport, headers=headers, json = dataValidate, verify=False)

        # modification user_validate et date_validate

        # refus de la note de frais
        if status == 'deny' :
            data = {
                "details": "Raison du refus : " + fake.sentence(nb_words=6),
                "notrigger" : 0
            }
            r = requests.post(urlReport + "/deny" , headers=headers, json=data, verify=False)

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
                r = requests.put(urlReport, headers=headers, json = dataDeny, verify=False)
                if r.status_code != 200 : 
                    if testing:
                        print('Erreur lors de la mise à jours du refus.')
                        print(r.text)
                
                if testing:
                    print('data refus update avec succés.')

            
        # approbation de la note de frais
        if status in ('approve', 'paid'):
            r = requests.post(urlReport + "/approve" , headers=headers, verify=False)
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
            r = requests.post(urlReport + "/" + str(status), headers=headers, json = data_cancel, verify=False)
            if r.status_code != 200 :
                if testing :  
                    print('Erreur lors du changement de statut de la note de frais en :', status, r.status_code)
                    print (r.text)
            else :
                if testing:
                    print('note de frais passée au statut : ' , status)

    # paiements des notes approuvées ??? utile?
    if status == 'paid':
        r = requests.get( urlDictionary + 'payment_types?active=1', headers=headers, verify=False)

    if status != "brouillon":
        r = requests.post(urlReport + "/validate", headers=headers, verify=False)
        if r.status_code == 200 and testing:
            print("Note validée")

        if status in ("approve", "paid"):
            r = requests.post(urlReport + "/approve", headers=headers, verify=False)
            if r.status_code == 200 and testing:
                print("Note approuvée")

        if status == "deny":
            r = requests.post(
                urlReport + "/deny",
                headers=headers,
                json={"details": fake.sentence(), "notrigger": 0},
                verify=False
            )
            if r.status_code == 200 and testing:
                print("Note refusée")

        if status == "cancel":
            r = requests.post(
                urlReport + "/cancel",
                headers=headers,
                json={"detail": fake.text()},
                verify=False
            )
            if r.status_code == 200 and testing:
                print("Note annulée")


    # PAIEMENT
    if status == "paid":
        r = requests.get(urlDictionary + "payment_types?active=1", headers=headers, verify=False)
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
            "datep":dateValidate.strftime('%Y-%m-%d'),
            "amount":totalAmountHT,
            "amounts": [totalAmountHT],
            "accountid":3
        }

        r = requests.post(urlReport + "/payments", headers = headers, json = data_payment, verify=False)

        if r.status_code != 200:
            print('erreur lors du paiement de la note de frais.')
            print(r.status_code)
            print(r.text)
        else :
            r = requests.post(urlReport + "/setpaid", headers=headers, verify=False)



# TEST
if __name__ == "__main__":
    for  i in range(10):
        print(
            generate_expense_report( 
                dateCreate= fake.date_this_year(before_today=True), testing = True)
    )


# paid => probleme sur les valeurs API
