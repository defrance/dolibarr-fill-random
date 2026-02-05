from datetime import timedelta
import random
import string
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# pour gérer les warnings de certificat SSL
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

from dolibarr_api import *
from utils import *

def generate_timekeeper(testing):
    url = urlBase + "timekeeprapi/"
    urlPlanned = url + "planned/"
    urlSpent = url + "spent/"
    urlTickets = urlBase + "tickets"
    urlInterventions = urlBase + "interventions"

    # Récupération des Tickets
    try:
      r =requests.get(urlTickets, headers = headers)
      print(r.status_code)
      dataTickets = r.json()
      
      if testing :
            print("Nombre de tickets :")
            print(len(dataTickets))
    
    except Exception as e:
       print(r.status_code)
       print(r.text)
       print(e)

    # Récupération des interventions

if __name__ == "__main__":
    print( 
        generate_timekeeper(testing = True
                              ))
    
"""
{
"fk_element" : 1,
"elementtype": "ticket" "
	ficheinter",
"element_duration": 4680,
"fk_user": 1,
"element_date": 1770249600
}
"""
