
import random
import requests
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from dolibarr_api import *
from utils import *

def generate_project(dateCreate, retDataUser, retDataThirdParties, testing=False):

    # DATA DE BASE

    urlProjects = urlBase + "projects/"
    urlTasks = urlBase + "tasks"

    dateCreateWithTime = dateCreate + timedelta(
        hours=random.randint(6, 19),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

    dateStart = fake.date_time_between(start_date=dateCreate, end_date=dateCreate + timedelta(days=30))
    dateEnd = fake.date_time_between(start_date=dateStart, end_date=dateStart + timedelta(days=180))

    dateStartTs = int(dateStart.timestamp())
    dateEndTs = int(dateEnd.timestamp())

    projectStatus = random.choice([0, 1, 2])  # draft / open / closed

    dataProject = {
        "ref": "auto",
        "title": fake.catch_phrase(),
        "description": fake.text(200),
        "date_start": dateStartTs,
        "date_end": dateEndTs,
        "socid": get_random_client(retDataThirdParties),
        "usage_task": 1,
        "usage_bill_time": 0,
        "budget_amount": random.randint(500, 10000),
        "status": projectStatus,
        "public": 1
    }

    r = requests.post(urlProjects, headers=headers, json=dataProject)
    if r.status_code != 200:
        print("Erreur création projet", r.text)
        return None

    projectID = get_created_id(r)


    # UPDATE POST-CREATION
 
    requests.put(
        urlProjects + str(projectID),
        headers=headers,
        json={
            "date_c": dateCreateWithTime.strftime("%Y-%m-%d %H:%M:%S"),
            "note_private": fake.text(200),
            "note_public": fake.text(200),
        }
    )

    # CONTACTS DU PROJET

    projectContacts = []
    urlProjectContacts = urlProjects + f"{projectID}/contacts"

    # Contacts INTERNES
    for _ in range(random.randint(0, nbInternalContactMax)):
        user = get_random_user(retDataUser)

        contact = {
            "fk_socpeople": user["id"],
            "type_contact": random.choice(["PROJECTLEADER", "PROJECTCONTRIBUTOR"]),
            "source": "internal"
        }

        r = requests.post(urlProjectContacts, headers=headers, json=contact)
        if r.status_code == 200:
            projectContacts.append(contact)

    # Contacts EXTERNES
    for _ in range(random.randint(0, nbExternalContactMax)):
        socid = get_random_client(retDataThirdParties)
        socpeople = fill_socpeople(socid)

        if not socpeople:
            continue

        contact = {
            "fk_socpeople": random.choice(socpeople)["id"],
            "type_contact": "PROJECTCONTRIBUTOR",
            "source": "external"
        }

        r = requests.post(urlProjectContacts, headers=headers, json=contact)
        if r.status_code == 200:
            projectContacts.append(contact)

  
    # TÂCHES (INTERNES UNIQUEMENT)

    for _ in range(random.randint(0, nbNewMaxTask)):

        taskStatus = random.choice([0, 1, 2, 3])

        dateTaskC = fake.date_time_between(dateCreate, dateEnd)
        dateTaskO = fake.date_time_between(dateTaskC, dateEnd)
        dateTaskE = fake.date_time_between(dateTaskO, dateEnd)

        r = requests.post(urlTasks, headers=headers, json={
            "ref": "auto",
            "fk_project": projectID,
            "label": fake.catch_phrase(),
            "description": fake.text(200),
            "date_start": int(dateTaskO.timestamp()),
            "date_end": int(dateTaskE.timestamp()),
            "planned_workload": random.randint(1, 20) * 3600,
            "status": 0
        })

        if r.status_code != 200:
            continue

        taskID = get_created_id(r)

        # Contacts TÂCHE → internes seulement
        internalContacts = [c for c in projectContacts if c["source"] == "internal"]

        for c in random.sample(internalContacts, min(len(internalContacts), random.randint(0, 3))):
            requests.post(
                urlBase + f"tasks/{taskID}/contacts",
                headers=headers,
                json={
                    "fk_socpeople": c["fk_socpeople"],
                    "type_contact": "TASKEXECUTIVE",
                    "source": "internal"
                }
            )

        # POINTAGES (USERS ONLY)

        for _ in range(random.randint(0, nbNewMaxTaskTime)):

            userId = random.choice(internalContacts)["fk_socpeople"] if internalContacts else 0

            requests.post(
                urlBase + f"tasks/{taskID}/addtimespent",
                headers=headers,
                json={
                    "date": fake.date_time_between(dateTaskO, dateTaskE).strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": random.randint(300, 3600),
                    "user_id": userId,
                    "progress": random.randint(0, 100),
                    "note": fake.sentence(8)
                }
            )

        # update statut final
        requests.put(
            urlBase + f"tasks/{taskID}",
            headers=headers,
            json={"status": taskStatus}
        )

    if testing:
        print(f"Projet {projectID} créé avec succès.")

    return projectID


# Test unitaire

if __name__ == "__main__":

    for i in range(10):
        print(generate_project(
            dateCreate = fake.date_this_decade(),
            testing=True))