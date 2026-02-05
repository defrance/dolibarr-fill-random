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
    try:
      r =requests.get(urlPlanned, headers = headers)
      print(r.status_code)
    except Exception as e:
       print(r.status_code)
       print(r.text)
       print(e)


if __name__ == "__main__":
    print( 
        generate_timekeeper(testing = True
                              ))