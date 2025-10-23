
"""             
def generate_opportunities(dateCreate):
    url = urlBase + "projects"

    dateCreation = dateCreate.strftime('%Y-%m-%d') # fonctionne pas
    dateStart = dateCreate.timestamp()
    dateEnd = dateStart + random.randint(5*24*3600, 30*24*3600)
    #deltaDate = dateEnd - dateStart
    #randomDays = random.randrang(deltaDate.days + 1)
    #dateEvent = dateStart + timedelta(days=randomDays)
    now = datetime.now()
    diffYears =(now - dateCreate).days /365.25


# Si la date de début de l'opportunité est plus ancienne que 2 ans, le projet est fermé
    if diffYears >= 2:
        status = 2  # closed
    
# Si la date de début de l'opportunité est entre 1 et 2 ans, le projet est ouvert ou fermé
    elif diffYears >= 1 and diffYears < 2:
        status = random.choice([1, 2])
# Si la date de début de l'opportunité est inférieure à 1 an, le projet est ouvert ou brouillon ou fermé
    elif diffYears < 1:
        status = random.choice([0,1,2])  # opened ou closed
    
    # Référence produit alphanumérique
    ref = 'PJ' + dateCreate.strftime('%m%y') + '-' + str(random.randint(1, 9999)).zfill(4)

    if status == 2:
        # Choisir aléatoirement avant, pendant, ou après dateEnd
        choice = random.choice(["before", "equal", "after"])
        
        if choice == "before":
            # Entre 1 et 5 jours avant
            dateClose = dateEnd - random.randint(1*24*3600, 5*24*3600)
        elif choice == "after":
            # Entre 1 et 5 jours après
            dateClose = dateEnd + random.randint(1*24*3600, 5*24*3600)
        else:
            # Exactement égale
            dateClose = dateEnd
    else:
        dateClose = None  # Pas encore clôturée si statut < 2
    
    data = {
    #"fk_project": null,
    #"fk_soc": "5",
    #"tms": "2025-10-17 14:03:53",
    "date_start": dateStart,
    "date_end": dateEnd,
    "ref": "auto", 
    #"ref_ext": null,
    #"entity": "1",
    "title": fake.catch_phrase(),
    #"description": "",
    #"fk_user_creat": "1",
    #"fk_user_modif": null,
    #"public": "0",
    #"fk_statut": "1",
    "fk_opp_status": 4,
    "opp_percent": 60.00,
    #"fk_opp_status_end": null,
    "date_close":dateClose if status == 2 else None,
    #"fk_user_close": null,
    "note_private": fake.text(max_nb_chars=200),
    "note_public": fake.text(max_nb_chars=200),
    #"email_msgid": null,
    #"email_date": null,
    #"opp_amount": "0.00000000",
    #"budget_amount": "0.00000000",
    "usage_opportunity": 1,
    "usage_task": 1,
    #"usage_bill_time": "0",
    #"usage_organize_event": "0",
    #"date_start_event": null,
    #"date_end_event": null,
    #"location": null,
    #"accept_conference_suggestions": "0",
    #"accept_booth_suggestions": "0",
    #"max_attendees": null,
    "status": 1,
    #"price_registration": null,
    #"price_booth": null,
    #"model_pdf": null,
    #"ip": null,
    #"last_main_doc": null,
    #"import_key": null,
    #"extraparams": null
     # users assigned to the project (en attente API)   
    }

    r = requests.post(url, headers=headers, json=data)
    if r.status_code != 200:
        print("Erreur lors de la création de l'opportunité", r.status_code)
        print (r.text)
        return None
    else:
        print("Création de l'opportunité : ", data)
        print (r.text)

    return 1
"""



        #retDataProjects = fill_projects()

""""
    # Génération des opportunités
    if nbNewOpportunity > 0 and 'projet' in enabledModule:
    listOpportunityGen = gen_randow_following_date(yearToFill, nbNewOpportunity, max_interval = dateinterval)
    for dateOpportunity in listOpportunityGen:
        generate_opportunities(dateOpportunity)
        #retDataOpportunities = fill_opportunities()

    # Génération des tâches


if nbNewTask > 0 and 'projet' in enabledModule:

    for _ in range(nbNewTask):
        generate_tasks(24) # A modifier pour randomiser a partir des projets existants.
        #retDataTasks = fill_tasks()

    # Génération des temps de tâches
if nbNewTaskTime > 0 and 'projet' in enabledModule:

    for _ in range (nbNewTaskTime):
        generate_tasks_times(17)  # A modifier pour randomiser a partir des tâches existantes et affectées au projet.

        """



"""
- Projets
    - ameliorer random date
    - affectation utilisateurs
    - notes => probablement par update
    - date création => probablement par update

- Taches
    -date début
    -date fin
    - temps effectif => par update probablement
    - statut
    - temps estimé
    - % avancement
    - affectation utilisateur

- time spent
    - date
    - affectation utilisateur

- Opportunités
    - update projet pour transformer certains en opportunité

"""