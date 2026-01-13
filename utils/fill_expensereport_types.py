
import requests
from datetime import datetime, timedelta
from faker import Faker
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from dolibarr_api import *


def fill_expensereport_types():
    url = urlBase + "setup/dictionary/expensereport_types"
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code != 200:
        print('Erreur lors de la récupération des types de notes de frais', r.status_code)
        print (r.text)
        exit()
    retDataExpensereportTypes = r.json()
    return retDataExpensereportTypes

# Test unitaire
if __name__ == "__main__":
    print(fill_expensereport_types())