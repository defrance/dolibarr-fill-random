
import random
import requests
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from dolibarr_api import *
from utils import *

def generate_project(dateCreate, nbTasks, nbtasksTime, retDataUser, retDataThirdParties, testing):
    # url de création de projet
    urlProjects = urlBase + "projects/"
    # url de création de tâche
    urlTasks = urlBase + "tasks"


    # Générer la date de création du projet comme datetime avec heure aléatoire
    dateCreateWithTime = dateCreate + timedelta(hours=random.randint(6, 19), minutes=random.randint(0, 59), seconds=random.randint(0, 59))

    # Générer la date de début du projet comme datetime
    dateStart = fake.date_time_between(start_date=dateCreate, end_date=dateCreate + timedelta(days=30))
    dateStartTs  = dateStart.timestamp()

    # Générer la date de fin prévue comme datetime, entre dateStart et 180 jours après
    dateEnd = fake.date_time_between(start_date=dateStart, end_date=dateStart + timedelta(days=180))
    dateEndTs = dateEnd.timestamp()
    
    # Calculer la différence en jours par rapport à aujourd'hui
    dateNow = datetime.now()
    diffDaysEndNow = (dateNow - dateEnd).days
    diffDaysStartNow = (dateNow - dateStart).days

    projectStatus = 1

    # Si la date de début du projet est inférieure à 1 an, le projet est ouvert ou brouillon ou fermé
    if diffDaysEndNow < 183 and diffDaysStartNow <= 0:
        projectStatus = random.choice([0,1,2])  # Draft, Open, Closed
    elif diffDaysStartNow > 0:
        projectStatus = random.choice([0,1])  # Draft, Open
    else:
        projectStatus = 0  # Open
    
    # Si le statut du projet est "fermé"
    if projectStatus == 2:
        # Choisi aléatoirement si la date de cloture du projet est avant, égale, ou après la prévue de fin
        choice = random.choice(["before", "equal", "after"])
        
        # Entre 1 et 5 jours avant la date prévue de fin
        if choice == "before":
            dateClose = dateEnd - timedelta(days=random.randint(1, 5))
        
        # Entre 1 et 5 jours après la date prévue de fin
        elif choice == "after":
            max_days = (dateNow - dateEnd).days

            # au moins 1 jour pour éviter erreur
            if max_days < 1:
                max_days = 1  
                
            days_after = random.randint(1, min(5, max_days))
            dateClose = dateEnd + timedelta(days=days_after)
        # Exactement égale
        else:
            dateClose = dateEnd
    else:
        # Pas de date de clôture si le statut est < 2
        dateClose = None
    
    # Date de fermeture en timestamp
    dateCloseTs = dateClose.timestamp() if dateClose else None

    data = {
        "date_start": dateStartTs,
        "date_end": dateEndTs,
        "ref": "auto",
        "title": fake.catch_phrase(),
        "description": fake.text(max_nb_chars=200),
        "date_close":dateCloseTs if projectStatus == 2 else None,
        # suivis de tache (par défaut activé)
        "usage_task": "1",
        "budget_amount": random.randint(500, 10000),
        "socid": get_random_client(retDataThirdParties),
        # Facturation du temps (par défaut désactivé)
        "usage_bill_time": "0",
        "status": projectStatus,
        "public" : 1
    }

    r = requests.post(urlProjects, headers=headers, json=data)
    
    if r.status_code != 200:
        print("Erreur lors de la création du projet", r.status_code)
        print (r.text)
        return None
    
    else:
        # Gestion du format de l'ID dans la réponse      
        try:
            resp = r.json()
            projectID = resp["id"] if isinstance(resp, dict) else resp
        except Exception:
            projectID = int(r.text.strip())

        if testing:
            print("ID du projet créé:", projectID)    

        #Update pour ajouter les data non prises en compte à la création
        if testing:
            print("Update des données complémentaires du projet...")

        dataUpdate = {
            # Modification de la date de la création du projet pour qu'elle ne soit pas la date du jours mais la date de création transmisse
            "date_c": dateCreateWithTime.strftime("%Y-%m-%d %H:%M:%S"),
            # Ajout de fausses notes
            "note_private": fake.text(max_nb_chars=200),
            "note_public": fake.text(max_nb_chars=200),
        }

        rU = requests.put(urlBase + "projects/" + str(projectID), headers=headers, json=dataUpdate)
        if rU.status_code != 200:
            print("Erreur lors de la mise à jour du projet", rU.status_code)
            print (rU.text)
            return None 
        else:
            if testing:
                print("Mise à jour du projet terminée.")

    # Association user au projet
    if testing:
        print("Ajout des contacts du projet ....")

    urlContactProject = urlBase + "projects/" + str(projectID) + "/contacts"
    projectContacts = []
    taskContacts = []

    if nbNewMaxContact > 0:
    # Défini un nombre d'user pour le projet
        nbProjectContacts = random.randint(1, nbNewMaxContact)
        if nbProjectContacts > 0:
            for i in range (nbProjectContacts):

                source = random.choice(['internal','external'])
                typeContact = random.choice(["PROJECTCONTRIBUTOR","PROJECTLEADER"]) # a randomiser depuis le dictionnaire

                # Si contact est interne
                if source == 'internal':
                    randomId =  get_random_user(retDataUser)['id']
                # Si le contact est externe
                elif source =="external":
                    randomId = get_random_client(retDataThirdParties)
                # Si erreur sur la source
                else:
                    print("source du contact invalide.")
                    return None
            
                # Association du contact avec son ID
                try:
                    dataContact = {
                        "fk_socpeople":randomId, #Required -  (integer): Id of thirdparty contact (if source = 'external') or id of user (if source = 'internal') to link ,
                        # faire random get_random_type_contact
                        "type_contact": typeContact, #Required "PROJECTCONTRIBUTOR" - ou Type of contact (code). Must a code found into table llx_c_type_contact. For example: BILLING ,
                        "source": source, #Required  "external" or "internal" -  external=Contact extern (llx_socpeople), internal=Contact intern (llx_user) ,
                        }
                    if testing:
                        print(urlContactProject)

                    rC = requests.post(urlContactProject, headers=headers,json=dataContact)
                    if rC.status_code != 200:
                        print("Erreur lors de l'ajout du contact", source ," : ", rC.status_code)
                        print (rC.text)
                        return None 
                    
                    else:
                        if testing:
                            print("Ajout du contact ", source, " terminée.")
                    
                        #  Stock les contacts associés au projet
                        projectContacts.append(dataContact)
                        if testing:    
                            print(dataContact)

                except Exception as e:
                    print("Erreur lors de l'ajout du contact ", source," au projet :", str(e))
                    return None   

            if testing:
                print("contacts du projet :")
                print(projectContacts)
        
        else:
            print("pas de contact associé au projet.")

    # Création des tâches associées au projet si le nombre de tâches est correct
    if nbTasks >= 0:
        if testing:
            print("Création du projet terminée, création des tâches associées...")

        # On crée un nombre aléatoire de tâches entre 0 et nbTasks par projet
        nbProjectContacts = random.randint(0, nbTasks)
        if nbProjectContacts == 0:
            if testing:
                print("Aucune tâche créée pour ce projet.") 
        else:
            for i in range (nbProjectContacts):
                if testing:
                    print("Création de la tâche n°", i+1,"sur", nbProjectContacts)
            
                if projectStatus == 2: # project closed
                    taskStatus = 3 # task closed
                
                if projectStatus == 1: # project open
                    taskStatus = random.choice([0,1,2,3])

                if projectStatus == 0: # project draft
                    taskStatus = 0 # task draft
                
                dateTaskC = fake.date_time_between_dates(dateCreate, dateEnd)
                dateTaskO = fake.date_time_between_dates(dateTaskC, dateEnd)
                dateTaskE = fake.date_time_between_dates(dateTaskO, dateEnd)

                data = {
                    "ref": "auto", #auto 
                    "fk_project": projectID,

                    "date_start": dateTaskO.timestamp(),
                    "date_end":  dateTaskE.timestamp(),
                    "label": fake.catch_phrase(),
                    "description":fake.text(max_nb_chars=200),
                    "planned_workload":fake.random_int(min=1, max=20) * 3600, # en secondes
                    "note_private": fake.text(max_nb_chars=200),
                    "note_public": fake.text(max_nb_chars=200),
                    "status": "0" # initial status draft, will be updated juste après
                }

                r = requests.post(urlTasks, headers=headers, json=data)
                if r.status_code != 200:
                    print("Erreur lors de la création de la tâche n°", i+1,".", r.status_code)
                    print (r.text)
                    return None
                else:
                
                    # on récupère l'ID de la tâche créée
                    try:
                        resp = r.json()
                        taskID = resp["id"] if isinstance(resp, dict) else resp
                    except Exception:
                        taskID = int(r.text.strip())

                    if testing:
                        print("ID de la tâche créée:", taskID)

                    # Ajout de contact à la tâche parmi les contact du projet
                    taskContacts = []
                    if len(projectContacts) > 0:
                        #Choisi un nombre aléatoire de contact à ajouter à la tache entre 1 et le nombre de contact du projet
                        nc =random.randint(1, nbProjectContacts)

                        for i in range(nc):
                            taskContact = random.choice(projectContacts)
                            if testing:
                                print(dataContact)
                            dataContact = {
                                "fk_socpeople": taskContact["fk_socpeople"],
                                "type_contact": random.choice(["TASKCONTRIBUTOR", "TASKEXECUTIVE"]),
                                "source":taskContact["source"]
                            }

                            r = requests.post(urlBase + "tasks/"+ str(taskID)+ "/contacts", headers=headers, json=dataContact)
                        
                            if r.status_code !=200:
                                print("erreur lors de l'ajout du contact à la tâche")
                        
                            else:
                                if testing:
                                    print("contact ajouté à la tâche.")
                                #  Stock les contacts associés à la tâche
                                taskContacts.append(dataContact)

                        if testing:
                            print("contacts associés à la tâche :")
                            print(taskContacts)
                    
                    # TODO ajouter l'utilsateur créateur de la tâche dans les contacts de la tâche s'il n'y est pas déjà
                    # sinon on risque de ne pas pouvoir mettre à jour la date de création de la tâche

                    dataUpdate = {
                        "date_c": dateTaskC.timestamp(),
                        "status": taskStatus
                    }

                    r = requests.put(urlBase + "tasks/"+ str(taskID), headers=headers, json=dataUpdate)
                    if r.status_code == 403:
                        print("403 : Not allowed to update task", i+1)
                    elif r.status_code != 200:
                        print("Erreur lors de la mise à jour de la date de création de la tâche n°", i+1,".", r.status_code)
                        print (r.text)
                        return None

                    if testing:
                        print(dataUpdate)
                        print("Maj de la tâche n°", str(taskID)," terminée. Création des pointages associés...")

                    # Si la tâche est en cours ou clôturé :
                    if taskStatus > 0:

                        urlTasksTime = urlBase + "tasks/"+ str(taskID) + "/addtimespent"
            
                        # on crée des pointages associés à la tâche 
                        if nbtasksTime < 0:
                            print("Nombre de pointage incorrect. Aucun pointage créé.")
                            return None     
                        else:
                            ntt = random.randint(0, nbtasksTime)

                        if ntt == 0:
                            if testing:
                                print("Aucun pointage créé pour cette tâche.")
                        
                        else:
                            for j in range (ntt):
                                if testing:
                                    print("Création du pointage n°", j+1,"sur task ", taskID)

                                randomDate = fake.date_time_between_dates(dateTaskO, dateTaskE)
                        
                                # Gestion de l'user associé au pointage
                                if len(taskContacts) > 0:
                                    userId = random.choice(taskContacts)['fk_socpeople']
                                else:
                                    # Si pas de contact associé à la tâche alors le pointage est attribué à l'user connecté
                                    userId = 0

                                data = {
                                    "date" : randomDate.strftime("%Y-%m-%d %H:%M:%S"),
                                    "duration": fake.random_int(min=60*5, max=3600), #  (integer): Duration in seconds (3600 = 1h) ,
                                    "user_id" : userId, # (integer, optional): User (Use 0 for connected user).
                                    "note" : fake.sentence(nb_words=10), # (string, optional): Note
                                    "progress" :fake.random_int(min=0, max=100)  # (integer, optional): Progress percentage (0-100)
                                }

                                r = requests.post(urlTasksTime, headers=headers, json=data)
    
                                if r.status_code != 200:
                                    print("Erreur lors de la création du pointage", r.status_code)
                                    print (r.json())
                                    return None
                                else:
                                    if testing:
                                        print("Création du pointage :  ", data)
                    continue
    else:
        print("Nombre de tâches incorrect. Aucune tâche créée.")
        return None
    
        # Si la date de fin du projet prévue est plus ancienne que 1 an, le projet est fermé
    if diffDaysEndNow > 365:
        projectStatus = 2  # closed 

    # Si la date de fin prévue du projet est entre 6 mois et 1 ans et la date début du projet est antérieure à la date du jour,
    # le projet est ouvert ou fermé de façon aléatoire
    elif diffDaysEndNow >= 183 and diffDaysEndNow <= 365:
        projectStatus = random.choice([1, 2])

    # et on change le statut du projet
    if projectStatus == 2: # closed
        dataUpdate = {
            "status": projectStatus
        }

        rU = requests.put(urlBase + "projects/" + str(projectID), headers=headers, json=dataUpdate)
        if rU.status_code != 200:
            print("Erreur lors de la mise à jour du projet", rU.status_code)
            print (rU.text)
            return None 
        else:
            if testing:
                print("Mise à jour du projet terminée.")




# Test unitaire

if __name__ == "__main__":

    for i in range(20):
        print(generate_project(
            dateCreate = fake.date_this_decade(),
            nbTasks=10,
            nbtasksTime=10,
            retDataUser= fill_users(),
            retDataThirdParties= fill_thirdparties(),
            testing=True))