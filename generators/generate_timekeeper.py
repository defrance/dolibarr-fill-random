from datetime import datetime, timedelta, date
import random
import string
import requests
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# pour gérer les warnings de certificat SSL
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

from dolibarr_api import *
from utils import *


def to_date(value):
    """Convertit une date Dolibarr (int / str / datetime / date) en datetime.date"""
    if isinstance(value, int):
        return datetime.fromtimestamp(value).date()
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.split(" ")[0]).date()
        except ValueError:
            return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def generate_timekeeper(nbMaxNewTimeSpentByTicket, nbMaxNewTimePlannedByTicket, NbMaxNewTimeSpentByIntervention, nbMaxNewTimePlannedByIntervention, testing):
    url = urlBase + "timekeeprapi/"
    urlPlanned = url + "planned/"
    urlSpent = url + "spent/"
    urlTickets = urlBase + "tickets/"
    urlInterventions = urlBase + "interventions/"
    timeSpentId = None

    today = datetime.now().date()

    # Récupération des Tickets
    try:
        r = requests.get(urlTickets, headers=headers)
        dataTickets = r.json()

        if testing:
            print("Nombre de tickets :")
            print(len(dataTickets))

    except Exception as e:
        print(r.status_code)
        print(r.text)
        print(e)
        return

    # Récupération des interventions
    try:
        r = requests.get(urlInterventions, headers=headers)
        dataInterventions = r.json()

        if testing:
            print("Nombre d'interventations :")
            print(len(dataInterventions))

    except Exception as e:
        print(r.status_code)
        print(r.text)
        print(e)

    # Récupération users
    try:
        dataUsers = fill_users()

        if testing:
            print("Nombre d'utilisateurs :")
            print(len(dataUsers))

    except Exception as e:
        print(e)
        return

    # Générateur temps plannifiés 
    def generate_timePlanned(d) :
            
        for i in range(random.randint(0, nbMaxTimePlanned)):
                data = {
                    "fk_element": d.get('id'),
                    "elementtype": elementType,
                    "element_duration": random.choice([
                                                        1800,   # 30 min
                                                        2700,   # 45 min
                                                        3600,   # 1h
                                                        5400,   # 1h30
                                                        7200,   # 2h
                                                        9000,   # 2h30
                                                        10800,  # 3h
                                                        12600,  # 3h30
                                                        14400   # 4h
                                                        ]),
                }

                try:
                    r = requests.post(urlPlanned, headers=headers, json=data)

                    if testing:
                        print(f"temps plannifié créé pour {elementType} : {d.get('ref')}")
                        print(r.text)

                except Exception as e:
                    print(r.status_code)
                    print(r.text)
                    print(e)

    # generateur temps consommées 

    def generate_timeSpent(d):

            rawDateCreate = d.get('datec')
            rawDateEnd = d.get('date_close')

            dateCreate = to_date(rawDateCreate)
            dateEnd = to_date(rawDateEnd) or today

        # limite date de fin à aujourd’hui
            dateEndEffective = min(dateEnd, today)

        # sécurité ordre des dates
            if dateCreate > dateEndEffective:
                dateCreate, dateEndEffective = dateEndEffective, dateCreate

        # génération date Faker
            if dateCreate == dateEndEffective:
                dateTimeSpentPython = dateEndEffective

            if not dateCreate:
                return

            else:
                dateTimeSpentPython = fake.date_between_dates(
                    date_start=dateCreate,
                    date_end=dateEndEffective
            )

            # conversion timestamp
            elementDateApi = int(
                datetime.combine(
                    dateTimeSpentPython,
                    datetime.min.time()
                ).timestamp()
            )

            # récupération des lignes
            """            line_id = None
            lines = d.get("lines",[])

            if not lines:
                return

            random_line = random.choice(lines)
            line_id = random_line.get("id")
            """
            
            for i in range(random.randint(0,  nbMaxTimeSpent)):

            # Définition userId

                fkUser = get_random_user_id(dataUsers)

                if testing:
                    print(f"IdUser : {fkUser['id']}")

                data = {
                    "fk_element": d.get('id'),
                    "elementtype": elementType,
                    "element_duration": random.choice([
                                                        1800,   # 30 min
                                                        2700,   # 45 min
                                                        3600,   # 1h
                                                        5400,   # 1h30
                                                        7200,   # 2h
                                                        9000,   # 2h30
                                                        10800,  # 3h
                                                        12600,  # 3h30
                                                        14400   # 4h
                                                        ]),
                    "fk_user": fkUser,
                    "element_date": elementDateApi,
                    #"intervention_line_id" : line_id
                }

                try:
                    r = requests.post(urlSpent, headers=headers, json=data)

                    if testing:
                        print(f"temps consommé créé pour {elementType} {d.get('ref')}")

                    """     
                        API renvoie de l'HTML (sur swagger ok)         
                        timeSpentId = r.text.strip()
                        print("id temps crée :")
                        print(timeSpentId) """

                except Exception as e:
                    print(r.status_code)
                    print(r.text)
                    print(e)
                
                # Update userId
                """

                if timeSpentId :
                    try:

                        dataUpdate = {
                            "fk_user": fkUser
                            }

                        r = requests.put(urlSpent + timeSpentId, headers = headers, json = dataUpdate)

                        if testing:
                            print('user id update')

                    except Exception as e:
                        print(r.status_code)
                        print(r.text)
                        print(e)
                """

    # Création temps consommés Tickets
    if nbMaxNewTimeSpentByTicket > 0 and dataTickets :
        for d in dataTickets :
            elementType = "ticket"
            nbMaxTimeSpent = nbMaxNewTimeSpentByTicket
            generate_timeSpent(d)

    # Création temps consommés Interventions
    if NbMaxNewTimeSpentByIntervention > 0 and dataInterventions :
        for d in dataInterventions :
            elementType = "fichinterdet"
            nbMaxTimeSpent = NbMaxNewTimeSpentByIntervention
            
            # Si intervention cloturée la rouvre pour ajouter les temps
            if d['statut'] == "3":
                try:
                    r = requests.post(urlInterventions + d['id'] + '/reopen', headers = headers)

                    generate_timeSpent(d)

                    r = requests.post(urlInterventions + d['id'] + '/validate', headers = headers)

                    r = requests.post(urlInterventions + d['id'] + '/close', headers = headers)

                except Exception as e:
                    print(r.status_code)
                    print(e)
            
            else:
                generate_timeSpent(d)
            
    # Création temps plannifiés Ticket
    if nbMaxNewTimePlannedByTicket > 0 and dataTickets:
        for d in dataTickets:
            elementType = "ticket"
            nbMaxTimePlanned = nbMaxNewTimePlannedByTicket
            generate_timePlanned(d)

    # Création temps plannifiés Interventions
    if nbMaxNewTimePlannedByIntervention > 0 and dataInterventions:
        for d in dataInterventions:
            elementType = "fichinterdet"
            nbMaxTimePlanned = nbMaxNewTimePlannedByIntervention
            # Si intervention cloturée la rouvre pour ajouter les temps
            if d['statut'] == "3":
                try:
                    r = requests.post(urlInterventions + d['id'] + '/reopen', headers = headers)

                    generate_timePlanned(d)

                    r = requests.post(urlInterventions + d['id'] + '/validate', headers = headers)

                    r = requests.post(urlInterventions + d['id'] + '/close', headers = headers)

                except Exception as e:
                    print(r.status_code)
                    print(e)
            
            else:
                generate_timePlanned(d)     


if __name__ == "__main__":
    generate_timekeeper(
        nbMaxNewTimeSpentByTicket = 10,
        nbMaxNewTimePlannedByTicket = 10,
        NbMaxNewTimeSpentByIntervention = 10,
        nbMaxNewTimePlannedByIntervention = 10,
        testing = True
    )

# impossible de changer le userId du temps consommé.
# probleme affichage des temps plannifié sur les tickets et les interventions (mais ils sont bien créés)