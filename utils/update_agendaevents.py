
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

def update_agendaevent(id, testing = False):
    url = urlBase + 'agendaevents/' + str(id)

    data = {
        "percentage": 0,       # slot affecté
        'note_private' : fake.catch_phrase(),
    }

    r = requests.put(url, headers=headers, json=data, verify=False)
    if r.status_code != 200:
        print("Erreur lors de la mise à jour de l'évènement", r.status_code)
        print (r.text)
        return None
    else:
        if testing:
            print('Event  ' + str(id) + ' mis à jour avec succès.')

        data = r.json()
        return data


if __name__ == "__main__":
    print (update_agendaevent(120, True))