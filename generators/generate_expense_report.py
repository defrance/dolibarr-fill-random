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
        r = requests.get(urlConf, headers=headers)

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

    r = requests.post(url, headers=headers, json=data)
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

    r = requests.get(urlDictionary + "vat?actibr=1&fk_country=-1", headers=headers)
    vatrateList = r.json()

    r = requests.get(urlDictionary + "expensereport_types?active=1", headers=headers)
    typefeesList = r.json()

    # Ajout des lignes de frais
    urlAddLine = urlReport + "/line"

        typefee = random.choice(typefeesList)
        typefeeID = typefee["id"]
        typefeeCode = typefee["code"]
        vatrate = random.choice(vatrateList)["taux"]

        
        qty, value_unit = get_realistic_qty_price(typefeeCode)

        if testing:
            print(f"Type frais {typefeeCode} → qty = {qty}, value_unit = {value_unit} €")

        dataLine = {
            "comments": fake.text(max_nb_chars=100),
            "fk_project": fkProject,
            "qty": qty,
            "value_unit": value_unit,
            "fk_c_type_fees": typefeeID,
            "vatrate": vatrate,
            "date": fake.date_between_dates(dateStart, dateEnd).strftime("%Y-%m-%d"),
        }

        r = requests.post(urlReport + "/line", headers=headers, json=dataLine)
        if testing and r.status_code == 200:
            print("Ligne de frais ajoutée")

    
    # STATUT

    status = random.choice(["brouillon", "validate", "approve", "deny", "cancel", "paid"])

    if testing:
        print("Status initial :", status)

    if dateEnd > datetime.today().date():

        status = "brouillon"


    if status != "brouillon":

        r = requests.post(urlReport + "/validate", headers=headers)
        if r.status_code == 200 and testing:
            print("Note validée")

        if status in ("approve", "paid"):
            r = requests.post(urlReport + "/approve", headers=headers)
            if r.status_code == 200 and testing:
                print("Note approuvée")

        if status == "deny":
            r = requests.post(
                urlReport + "/deny",
                headers=headers,
                json={"details": fake.sentence(), "notrigger": 0},
            )
            if r.status_code == 200 and testing:
                print("Note refusée")

        if status == "cancel":
            r = requests.post(
                urlReport + "/cancel",
                headers=headers,
                json={"detail": fake.text()},
            )
            if r.status_code == 200 and testing:
                print("Note annulée")


    # PAIEMENT

    """    if status == "paid":
        r = requests.get(urlDictionary + "payment_types?active=1", headers=headers)
        paymentTypeList = r.json()

        fkTypePayment = random.choice(paymentTypeList)["id"]

        data_payment = {
            "fk_typepayment": fkTypePayment,
            "datepaid": datetime.date.today().strftime("%Y-%m-%d"),
            "amount": 200,
            "bank_account": 3,
        }

        r = requests.post(urlReport + "/payments", headers=headers, json=data_payment)
        if testing and r.status_code == 200:
            print("Paiement effectué")"""

    return expenseReportID

# TEST
if __name__ == "__main__":
    for i in range(10):
        generate_expense_report(
            dateCreate=fake.date_this_decade(before_today=True),
            testing=True,
        )
    for i in range(3):
        generate_expense_report(
            dateCreate=fake.date_this_year(before_today=True),
            testing=True,
        )
