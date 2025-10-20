import datetime
from faker import Faker
import random
import string
import requests
import string

from dolibarr_api import *

fake = Faker('fr_FR')



def generate_projects(dateCreate):

    dateStart = dateCreate.timestamp()
    dateCreation = dateCreate.strftime('%Y-%m-%d') # fonctionne pas
    dateEnd = dateStart + random.randint(5*24*3600, 30*24*3600)
    url = urlBase + "projects"

    # Référence produit alphanumérique
    ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    status = random.choice([0, 1, 2])  # 0=draft, 1=opened, 2=closed

    if status == 2:
        dateClose = dateEnd - random.randint(1*24*3600, 5*24*3600)
    data = {
        "ref": str(ref),
        #"fk_project": ,
        #"description": ,
        "title" : fake.sentence(nb_words=4),
        "date_start": dateStart,
        "date_end": dateEnd,
        "date_close": dateClose if status == 2 else None,
        #"datec": dateCreation, # fonctionne pas 
        "status": status,
        #"socid":
    }

    
    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print("Erreur lors de la création du projet", r.status_code)
        print (r.text)
        return None
    else:
        print("Création du projet : ", data)
        print (r.text)

    return 1


def generate_tasks():
    url = urlBase + "tasks"
    ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    data = {
        "ref":str(ref),
        "label": fake.sentence(nb_words=4),
        "fk_project": 24 # A modifier pour randomiser a partir des projets existants
    }

    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print("Erreur lors de la création de la tâche", r.status_code)
        print (r.text)
        return None
    else:
        print("Création de la tâche : ", data)
        print (r.text)

    return 1


# on mémorise l'heure de début de l'alimentation
start_time = datetime.now()
print("Début de l'alimentation à ", start_time.strftime('%Y-%m-%d %H:%M:%S'))
start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_time
print("Alimentation Initiale : ", duration)
print("Fin de l'alimentation à ", start_stop.strftime('%Y-%m-%d %H:%M:%S'))

nbNewProject = 0
nbNewTask = 5

# Génération des projets

if nbNewProject > 0 : # and 'project' in enabledModule:

    listProjectGen = gen_randow_following_date(yearToFill, nbNewProject, max_interval = dateinterval)
    for dateProject in listProjectGen:
        generate_projects(dateProject)


if nbNewTask > 0 : # and 'project' in enabledModule:

    for _ in range(nbNewTask):
        generate_tasks()

"""

public $statut; // 0=draft, 1=opened, 2=closed

project:
  new_project : 0
  new_task : 0
  new_task_time : 0

  # infos lies au projet
nbNewProject=config['project']['new_project']
nbNewTask=config['project']['new_task']
nbNewTaskTime=config['project']['new_task_time']

if nbNewFichinter > 0 and 'ficheinter' in enabledModule:
    listInterventionGen = gen_randow_following_date(yearToFill, nbNewFichinter, max_interval = dateinterval)
    for dateInter in listInterventionGen:
        fichinter = generate_interventionals(dateInter)


class Project:
	/**
	 * @var string[]       Mandatory fields, checked when create and update object
	 */
	public static $FIELDS = array(
		'ref',
		'title'
	);

"""