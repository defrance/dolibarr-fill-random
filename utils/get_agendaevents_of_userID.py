
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

def get_agendaevents_of_userID(id, sqlfilter, testing = False):
 url = urlBase + 'agendaevents?sortfield=t.datep&sortorder=ASC&limit=100&user_ids=' + str(id)
 if sqlfilter:
     url += '&sqlfilters=' +sqlfilter

 r = requests.get(url, headers=headers, verify=False)
 if r.status_code != 200:
        if testing:
            print('Erreur lors de la récupération des évènements du contactID ' + str(id), r.status_code)
            print (r.text)
        return None
 else:
    if testing:
            print('Event du contactID ' + str(id) + ' récupérés avec succès.')

    data = r.json()
    print ("Nombre d'évènements récupérés : ", len(data))
    return data


if __name__ == "__main__":
     filter = "(t.percent%3A%3D%3A-1)"
     print (get_agendaevents_of_userID(6, filter,   True))