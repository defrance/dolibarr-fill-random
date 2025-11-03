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


def generate_expense_report( dateStart, retDataUser, testing = False):
    url = urlBase + "expensereports"

    print (url)
    data = {
        "fk_user_author": get_random_user(retDataUser)['id'],
        "date_debut": dateStart.strftime('%Y-%m-%d'),
        "date_fin": fake.date_between_dates(dateStart, datetime.now()).strftime('%Y-%m-%d'),
    }

    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code != 200:
            print('Erreur lors de la création du note de frais', r.status_code)
            print (r.text)
            return None
        else:
            expenseReportID = r.text
            if testing :
                print("Note de frais créée avec l'ID : ", expenseReportID)
                r = requests.get(urlBase + "expensereports/" + str(expenseReportID), headers=headers)
                print("Détail de la note de frais :", r.json())

    except Exception as e:
        print("Erreur lors de la création du note de frais :", e)
        







# testing

if __name__ == "__main__":
    print(
        generate_expense_report( 
            dateStart= fake.date_this_month(before_today=True),
            retDataUser =fill_users(), testing = True)
    )