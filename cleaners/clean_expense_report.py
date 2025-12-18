import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

def clean_expense_report(testing):
    url = urlBase + "expensereports"

    r = requests.get(url, headers=headers, verify = False)

    if r.status_code != 200:
        print('Erreur lors de la récupération des notes de frais', r.status_code)
        print(r.text)
        exit()
    retDataExpenseReports = r.json()

    for report in retDataExpenseReports :
        try:
            r = requests.delete(url + "/" + report['id'], headers=headers)
            if testing:
                print("note de frais supprimée : ", report['id'])
            
        
        except :
            print("erreur lors de la suppression de la note de frais.", r.status_code)
            print(r.text)

    print("Suppression notes de frais terminée.")

if __name__ == "__main__":
    clean_expense_report(testing=True)