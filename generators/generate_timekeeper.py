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
    urlTickets = urlBase + "tickets"
    urlInterventions = urlBase + "interventions"

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

    # Création temps plannifiés pour chaque Tickets
    if nbMaxNewTimePlannedByTicket > 0 and dataTickets:

        for t in dataTickets:
            for i in range(random.randint(1, nbMaxNewTimePlannedByTicket)):
                data = {
                    "fk_element": t.get('id'),
                    "elementtype": "ticket",
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
                    print(f"temps plannifié créé pour ticket {t.get('id')}")
                    print(r.text)

            except Exception as e:
                print(r.status_code)
                print(r.text)
                print(e)

    # Création temps consommées pour chaque Tickets
    if nbMaxNewTimeSpentByTicket > 0 and dataTickets:

        for t in dataTickets:
            rawDateCreate = t.get('datec')
            rawDateEnd = t.get('date_close')

            dateCreate = to_date(rawDateCreate)
            dateEnd = to_date(rawDateEnd) or today

            if not dateCreate:
                continue

        # limite date de fin à aujourd’hui
            dateEndEffective = min(dateEnd, today)

        # sécurité ordre des dates
            if dateCreate > dateEndEffective:
                dateCreate, dateEndEffective = dateEndEffective, dateCreate

        # génération date Faker
            if dateCreate == dateEndEffective:
                dateTimeSpentPython = dateEndEffective

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


            for i in range(random.randint(1, nbMaxNewTimeSpentByTicket)):

            # Définition userId

                fkUser = get_random_user_id(dataUsers)

                if testing:
                    print(f"IdUser : {fkUser['id']}")

                data = {
                    "fk_element": t.get('id'),
                    "elementtype": "ticket",
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
                    "element_date": elementDateApi
                }

                try:
                    r = requests.post(urlSpent, headers=headers, json=data)

                    if testing:
                        print(f"temps consommé créé pour ticket {t.get('id')}")

                except Exception as e:
                    print(r.status_code)
                    print(r.text)
                    print(e)


if __name__ == "__main__":
    generate_timekeeper(
        nbMaxNewTimeSpentByTicket = 1,
        nbMaxNewTimePlannedByTicket = 1,
        NbMaxNewTimeSpentByIntervention = 3,
        nbMaxNewTimePlannedByIntervention = 3,
        testing = True
    )

# pas possible de changer le userId du temps consommé.
# probleme affichage des temps plannifié sur les tickets (mais ils sont bien créés)