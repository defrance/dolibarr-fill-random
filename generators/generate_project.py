from faker import Faker
import random
import string
import requests
import base64
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

fake = Faker('fr_FR')

def generate_project(dateCreate, nbTasks, nbtasksTime,nbContactByProject, retDataUser, retDataThirdParties, testing=False):
# url de création de projet
    urlProjects = urlBase + "projects"
    urlTasks = urlBase + "tasks"

# Générer dateCreate comme datetime avec heure aléatoire
    dateCreateWithTime = dateCreate + timedelta(hours=random.randint(6, 19), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
    

# Générer dateStart comme datetime
    dateStart = fake.date_time_between(start_date=dateCreate, end_date=dateCreate + timedelta(days=30))
    dateStartTs  = dateStart.timestamp()

# Générer dateEnd comme datetime, entre dateStart et 180 jours après
    dateEnd = fake.date_time_between(start_date=dateStart, end_date=dateStart + timedelta(days=180))
    dateEndTs = dateEnd.timestamp()
    
# Calculer la différence en années
    dateNow = datetime.now()
    diffDaysEndNow = (dateEnd - dateNow).days
    diffDaysStartNow = (dateStart - dateNow).days

# Si la date de fin du projet prévue est plus ancienne que 1 an, le projet est fermé
    if diffDaysEndNow > 365:
        status = 2  # closed 
# Si la date de fin prévue du projet est entre 6 mois et 1 ans et la date début du projet est passée le projet est ouvert ou fermé
    elif diffDaysEndNow >= 183 and diffDaysEndNow <= 365:
        status = random.choice([1, 2])
# Si la date de début du projet est inférieure à 1 an, le projet est ouvert ou brouillon ou fermé
    elif diffDaysEndNow < 183 and diffDaysStartNow <= 0:
        status = random.choice([0,1,2])  # Draft, Open, Closed
    elif diffDaysStartNow > 0:
        status = random.choice([0,1])  # Draft, Open
    else:
        status = 0  # Open
    
    if status == 2:
# Choisir aléatoirement avant, pendant, ou après dateEnd
        choice = random.choice(["before", "equal", "after"])
        
        if choice == "before":
# Entre 1 et 5 jours avant la date prévue de fin
            dateClose = dateEnd - timedelta(days=random.randint(1, 5))
        elif choice == "after":
# Entre 1 et 5 jours après la date prévue de fin
            max_days = (dateNow - dateEnd).days
            if max_days < 1:
                max_days = 1  # au moins 1 jour pour éviter erreur
            days_after = random.randint(1, min(5, max_days))
            dateClose = dateEnd + timedelta(days=days_after)
        else:
# Exactement égale
            dateClose = dateEnd
    else:
        dateClose = None  # Pas encore clôturée si statut < 2
    
    dateCloseTs  =dateClose.timestamp() if dateClose else None

    data = {
    #"fk_project": null,
    #"fk_soc": "5",
    "date_start": dateStartTs,
    "date_end": dateEndTs,
    "ref": "auto",
    #"ref_ext": null,
    #"entity": "1",
    "title": fake.catch_phrase(),
    "description": fake.text(max_nb_chars=200),
    #"fk_user_creat": "1",
    #"fk_user_modif": null,
    #"public": "0",
    #"fk_statut": "1",
    #"fk_opp_status": null,
    #"opp_percent": null,
    #"fk_opp_status_end": null,
    "date_close":dateCloseTs if status == 2 else None,
    #"fk_user_close": null,
    #"email_msgid": null,
    #"email_date": null,
    #"opp_amount": "0.00000000",
    #"budget_amount": "0.00000000",
    #"usage_opportunity": "0",
    #"usage_task": "1",
    #"usage_bill_time": "0",
    #"usage_organize_event": "0",
    #"date_start_event": null,
    #"date_end_event": null,
    #"location": null,
    #"accept_conference_suggestions": "0",
    #"accept_booth_suggestions": "0",
    #"max_attendees": null,
    "status": status,
    #"price_registration": null,
    #"price_booth": null,
    #"model_pdf": null,
    #"ip": null,
    #"last_main_doc": null,
    #"import_key": null,
    #"extraparams": null
     # users assigned to the project (en attente API)   
    }

    r = requests.post(urlProjects, headers=headers, json=data)
    if r.status_code != 200:
        print("Erreur lors de la création du projet", r.status_code)
        print (r.text)
        return None
    else:
            
# on récupère l'ID du projet créé
        try:
            resp = r.json()
            projectID = resp["id"] if isinstance(resp, dict) else resp
        except Exception:
            projectID = int(r.text.strip())
            print("ID du projet créé:", projectID)    


#Update pour ajouter les data pas prises en compte à la création
        print("Update des données complémentaires du projet...")
        try:
            dataUpdate = {
                "date_c": dateCreateWithTime.strftime("%Y-%m-%d %H:%M:%S"),
                "note_private": fake.text(max_nb_chars=200),
                "note_public": fake.text(max_nb_chars=200),
            }

            rU = requests.put(urlBase + "projects/" + str(projectID), headers=headers, json=dataUpdate)
            if rU.status_code != 200:
                print("Erreur lors de la mise à jour du projet", rU.status_code)
                print (rU.text)
                return None 
            else:
                print("Mise à jour du projet terminée.")
        except Exception as e:
            print("Erreur lors de la mise à jour du projet:", str(e))
            return None
        

# Association user au projet
        print("Ajout des users au projet ....")

        urlContactProject = urlBase + "dolismartprojectsapi/" + str(projectID) + "/contacts"
        projectContacts = []

        if nbContactByProject > 0:
# défini un nombre d'user pour le projet
            nt = random.randint(0,nbContactByProject)
            
# défini si le contact est un user ou un tiers


            for i in range (nt):
                source = random.choice(['internal','external'])
                typeContact = random.choice(["PROJECTCONTRIBUTOR","PROJECTLEADER"]) # a randomiser depuis le dictionnaire
                # Si contact est interne
                if source == 'internal':
                     randomId =  get_random_user(retDataUser)['id']
                elif source =="external":
                    randomId = get_random_client(retDataThirdParties)

                else:
                    print("source du contact invalide.")
                    return None
                
                try:
                    dataContact = {
                        "fk_socpeople":randomId, #Required -  (integer): Id of thirdparty contact (if source = 'external') or id of user (if source = 'internal') to link ,
                        # faire random get_random_type_contact
                        "type_contact": typeContact, #Required "PROJECTCONTRIBUTOR" - ou Type of contact (code). Must a code found into table llx_c_type_contact. For example: BILLING ,
                        "source": source, #Required  "external" or "internal" -  external=Contact extern (llx_socpeople), internal=Contact intern (llx_user) ,
                        #"notrigger": 0  #Optional
                        }

                    rC = requests.post(urlContactProject, headers=headers,json=dataContact)
                    if rC.status_code != 200:
                        print("Erreur lors de l'ajout du contact {source}", rC.status_code)
                        print (rC.text)
                        return None 
                    else:
                        print("Ajout du contact {source} terminée.")
                        #  Stock les contacts associés
                        print(dataContact)
                        projectContacts.append(dataContact)

                except Exception as e:
                    print("Erreur lors de l'ajout du contact {source} au projet :", str(e))
                    return None   

            if testing:
                print("contacts du projet :")
                print(projectContacts)


# Création des tâches associées au projet si le nombre de tâches est correct
        if nbTasks >= 0:

            print("Création du projet terminée, création des tâches associées...")

# On crée un nombre aléatoire de tâches entre 0 et nbTasks par projet
            nt = random.randint(0, nbTasks)
            if nt == 0:
                print("Aucune tâche créée pour ce projet.")
                return 1
            
            for i in range (nt):
                print("Création de la tâche n°", i+1,"sur", nt)

                dateC = fake.date_between_dates(dateCreate,dateEnd)
                dateO = fake.date_between_dates(dateC,dateNow)
                dateE = fake.date_between_dates(dateO,dateEnd)
                #voir pour ajouter possibilité que la tache depasse si le projet depasse la date limite.
                #dateV = fake.date_between_dates(dateE,dateEnd)

                data = {
                "ref": fake.unique.bothify(text=f"TASK-{projectID}-#####"),
                #"entity":"1",
                "fk_project": projectID, 
                #"fk_task_parent":"0",
                "datec":dateC.strftime("%Y-%m-%d"),
                # "tms":"2025-10-17 14:08:39",
                "dateo": dateO.strftime("%Y-%m-%d"),
                "datee": dateE.strftime("%Y-%m-%d"),
                # "datev":dateV,
                "label": fake.catch_phrase(),
                "description":fake.text(max_nb_chars=200),
                # "duration_effective":"10980",
                # "planned_workload":"36000",
                # "progress":"30",
                # "priority":"0",
                # "budget_amount":"0.00000000",
                # "fk_user_creat":"1",
                # "fk_user_modif":null,
                # "fk_user_valid":null,
                # "fk_statut":"2",
                "note_private": fake.text(max_nb_chars=200),
                "note_public": fake.text(max_nb_chars=200),
                # "rang":"0",
                # "model_pdf":null,
                # "import_key":null,
                # "billable":"0"}
                }

                # print("Création de la tâche: ", data)
                r = requests.post(urlTasks, headers=headers, json=data)
                if r.status_code != 200:
                    print("Erreur lors de la création de la tâche", r.status_code)
                    print (r.text)
                    return None
                else:
                    print("Création de la tâche terminée. Création des temps passés associés...")
                    if testing:
                        print('tache créée :')
                        print(data)
            # on récupère l'ID de la tâche créée
                    try:
                        resp = r.json()
                        taskID = resp["id"] if isinstance(resp, dict) else resp
                    except Exception:
                        taskID = int(r.text.strip())

                        print("ID de la tâche créée:", taskID)

                    urlTasksTime = urlBase + "tasks/"+ str(taskID) + "/addtimespent"
                
            # on crée des temps passés associés à la tâche 
                    if nbtasksTime < 0:
                        print("Nombre de temps passés incorrect. Aucun temps passé créé.")
                        return None     
                    else:
                        ntt = random.randint(0, nbtasksTime)
                        if ntt == 0:
                            print("Aucun temps passé créé pour cette tâche.")
                            continue

                        for j in range (ntt):
                            print("Création du temps passé n°", j+1,"sur", ntt)

                            randomDate = fake.date_between_dates(dateO, dateE)
                            randomTime = timedelta(
                                                    hours=random.randint(7, 19),
                                                    minutes=random.randint(0, 59),
                                                    seconds=random.randint(0, 59)
                                                    )
                            finalDatetime = datetime.combine(randomDate, datetime.min.time()) + randomTime

                            data = {
                                "date" : finalDatetime.strftime("%Y-%m-%d %H:%M:%S"), #  ajouter une heure random
                                "duration": fake.random_int(min=60*5, max=3600), #  (integer): Duration in seconds (3600 = 1h) ,
                                "user_id" : random.choice(projectContacts)['fk_socpeople'], # (integer, optional): User (Use 0 for connected user). A modifier pour randomiser a partir des utilisateurs existants et affectés au projet.
                                "note" : fake.sentence(nb_words=10) # (string, optional): Note
                            }
                            r = requests.post(urlTasksTime, headers=headers, json=data)
        
                            if r.status_code != 200:
                                print("Erreur lors de la création de la période", r.status_code)
                                print (r.json())
                                return None
                            else:
                                if testing:
                                    print("Création de la période: ", data)
                                continue
                        continue
        if nbTasks < 0:
           print("Nombre de tâches incorrect. Aucune tâche créée.")

# Test unitaire

if __name__ == "__main__":
    print(generate_project(
        dateCreate = fake.date_this_year(),
        nbTasks=10,
        nbtasksTime=10,
        nbContactByProject=10,
        retDataUser= fill_users(),
        retDataThirdParties= fill_thirdparties(),
        testing=True))