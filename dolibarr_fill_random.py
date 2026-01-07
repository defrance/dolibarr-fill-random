import random
import datetime
from tqdm import tqdm
import os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from dolibarr_api import *
from generators import *
from utils import *


def generate_with_error_handling(generator_func, date, *args, **kwargs):
    """
    Wrapper pour exécuter une fonction de génération avec gestion d'erreur
    """
    try:
        return generator_func(date, *args, **kwargs)
    except Exception as e:
        if testing:
            print(f"Erreur lors de la génération à la date {date}: {e}")
        return None


# On mémorise l'heure de début de l'alimentation totale
start_time = datetime.now()
print("Début de l'alimentation à ", start_time.strftime('%Y-%m-%d %H:%M:%S'))

# Affiche des messages de tests
if testing:
    testToggle = True
else :
    testToggle = False

# Récupération des modules actifs coté Dolibarr
enabledModule = get_enabled_modules()
if testing:
    print ("Liste des modules activés dans Dolibarr")
    print (enabledModule)

# Création des catégories
if newCategory > 0 and 'categorie' in enabledModule:
    for i in range(random.randint(1, newCategory)):
        generate_category("product", testToggle)
    for i in range(random.randint(1, newCategory)):
        generate_category("customer", testToggle)
    for i in range(random.randint(1, newCategory)):
        generate_category("contact", testToggle)
    for i in range(random.randint(1, newCategory)):
        generate_category("ticket", testToggle)

retDataCategProduct = fill_categories("product")
retDataCategCustomer = fill_categories("customer")
retDataCategContact = fill_categories("contact")

if 'ticket' in enabledModule:
    retDataCategTicket = fill_categories("ticket")

if nbNewWarehouse > 0 and 'stock' in enabledModule:
    listWareHouseGen = gen_random_following_date(yearToFill, nbNewWarehouse, max_interval = dateinterval)
    for dateCreate in listWareHouseGen:
        warehouse = generate_warehouse(dateCreate, testToggle)

# On remplit les entrepots et les utilisateurs pour les alimentations aléatoires
retDataWarehouse = fill_warehouses()

if nbNewUser > 0:
    listUserGen = gen_random_following_date(yearToFill, nbNewUser, max_interval = dateinterval)
    for dateCreate in listUserGen:
        product = generate_user(dateCreate, testToggle)

retDataUser = fill_users()

if nbNewBank > 0 and 'banque' in enabledModule:
    listBankGen = gen_random_following_date(yearToFill, nbNewBank, max_interval = dateinterval)
    for dateCreate in listBankGen:
        bank = generate_bank(dateCreate, testToggle)

if 'banque' in enabledModule:
    retDataBank = fill_banks()
    retDataPayment = fill_payement_types()

# On affiche la durée de l'alimentation
start_stop = datetime.now()
duration = start_stop - start_time
print("Alimentation Initiale : ", duration)
start_prev = datetime.now()

# On crée les clients avant les produits pour associer les prix fournisseurs si besoin
if nbNewClient > 0:
    listClientGen = gen_random_following_date(yearToFill, nbNewClient, max_interval = dateinterval)
    for dateCreate in listClientGen:
        client = generate_customer(dateCreate, retDataCategContact, retDataCategCustomer, enabledModule, testToggle)

if nbNewProduct > 0:
    listProductGen = gen_random_following_date(yearToFill, nbNewProduct, max_interval = dateinterval)
    for dateCreate in listProductGen:
        product = generate_product(dateCreate, retDataWarehouse, retDataCategProduct, enabledModule, testToggle)

retDataProduct = fill_products()

retDataThirdParties = fill_thirdparties("customer")

if createSupplier == 1  and 'fournisseur' in enabledModule:
    retDataFournisseur = fill_thirdparties("supplier")

# on affiche la durée de l'alimentation
start_stop = datetime.now()

duration = start_stop - start_prev
print("Durée Alimentation Tiers et produits : ", duration)

# Alimentation des projets 
start_prev = datetime.now()

if nbNewProject > 0 and 'projet' in enabledModule:
    listProjectGen = gen_random_following_date(yearToFill, nbNewProject, max_interval = dateinterval)
    for dateProject in listProjectGen:
        generate_project(dateProject, retDataUser, retDataThirdParties, testToggle)

retDataProjects = fill_projects()

start_stop = datetime.now()

duration = start_stop - start_prev
print("Durée Alimentation Projet et tâches : ", duration)

# ALimentation des factures, commandes et devis EN PARALLÈLE
start_prev = datetime.now()

# Préparer les listes de dates pour chaque type de génération
listFactureGen = [] if nbNewBill <= 0 or 'facture' not in enabledModule else gen_random_following_date(yearToFill, nbNewBill, max_interval = dateinterval)
listOrderGen = [] if nbNewOrder <= 0 or 'commande' not in enabledModule else gen_random_following_date(yearToFill, nbNewOrder, max_interval = dateinterval)
listProposalGen = [] if nbNewProposal <= 0 or 'propal' not in enabledModule else gen_random_following_date(yearToFill, nbNewProposal, max_interval = dateinterval)

# Soumettre TOUTES les tâches (factures, commandes, devis) au pool en même temps
# pour qu'elles s'exécutent vraiment en parallèle
print(f"Utilisation de {max_workers} workers pour la parallélisation")
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    all_futures = []
    
    # Soumettre toutes les factures
    for dateFact in listFactureGen:
        all_futures.append({
            'future': executor.submit(
                generate_with_error_handling,
                generate_invoice,
                dateFact,
                retDataPayment,
                retDataBank,
                retDataProduct,
                retDataThirdParties,
                retDataUser,
                testToggle
            ),
            'type': 'facture'
        })
    
    # Soumettre toutes les commandes
    for dateOrder in listOrderGen:
        all_futures.append({
            'future': executor.submit(
                generate_with_error_handling,
                generate_order,
                dateOrder,
                retDataProduct,
                retDataThirdParties,
                retDataWarehouse,
                retDataUser,
                testToggle
            ),
            'type': 'commande'
        })
    
    # Soumettre tous les devis
    for dateProposal in listProposalGen:
        all_futures.append({
            'future': executor.submit(
                generate_with_error_handling,
                generate_proposal,
                dateProposal,
                retDataThirdParties,
                retDataProduct,
                retDataUser,
                testToggle
            ),
            'type': 'devis'
        })
    
    # Compteurs pour le suivi
    completed = {'facture': 0, 'commande': 0, 'devis': 0}
    total = {'facture': len(listFactureGen), 'commande': len(listOrderGen), 'devis': len(listProposalGen)}
    
    # Attendre la complétion avec barre de progression globale
    for item in tqdm(
        all_futures,
        desc="Création factures/commandes/devis",
        unit="doc"
    ):
        item['future'].result()
        completed[item['type']] += 1
    
    # Afficher les statistiques
    print(f"  → Factures: {completed['facture']}/{total['facture']}, "
          f"Commandes: {completed['commande']}/{total['commande']}, "
          f"Devis: {completed['devis']}/{total['devis']}")

start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_prev
print("Durée Alimentation Factures, Commandes et Devis (en parallèle) : ", duration)

# Alimentation des contrats et interventions
start_prev = datetime.now()

if nbNewContract > 0 and 'contrat' in enabledModule:
    listContractGen = gen_random_following_date(yearToFill, nbNewContract, max_interval = dateinterval)
    for dateContract in listContractGen:
        contract = generate_contract(dateContract, retDataThirdParties, retDataProduct, retDataUser, testToggle)

if nbNewFichinter > 0 and 'ficheinter' in enabledModule:
    listInterventionGen = gen_random_following_date(yearToFill, nbNewFichinter, max_interval = dateinterval)
    for dateInter in listInterventionGen:
        fichinter = generate_intervention(dateInter, retDataThirdParties, enabledModule, testToggle)

start_stop = datetime.now()
# on affiche la durée de l'alimentation
duration = start_stop - start_prev
print("Durée Alimentation Contrat et intervention : ", duration)

# Alimentation des tickets et articles
start_prev = datetime.now()

if nbNewTicket > 0  and 'ticket' in enabledModule:
    listTicketGen = gen_random_following_date(yearToFill, nbNewTicket, max_interval = dateinterval)
    for dateTicket in listTicketGen:
        ticket = generate_ticket(dateTicket, retDataThirdParties, testToggle)

if nbNewKnowledge > 0  and 'knowledgemanagement' in enabledModule:
    listArticleGen = gen_random_following_date(yearToFill, nbNewKnowledge, max_interval = dateinterval)
    for dateknowledge in listArticleGen:
        ticket = generate_knowledge(dateknowledge, testToggle)

start_stop = datetime.now()
duration = start_stop - start_prev
print("Alimentation Tickets et articles : ", duration)

# Alimentation des congés/absences
start_prev = datetime.now()

if nbHoliday > 0  and 'holiday' in enabledModule:
    listHolidayGen = gen_random_following_date(yearToFill, nbHoliday, max_interval = dateinterval)
    for dateHoliday in listHolidayGen:
        holiday = generate_holiday(dateHoliday, testToggle)

start_stop = datetime.now()
duration = start_stop - start_prev
print("Alimentation congés : ", duration)

# Alimentation des notes de frais
start_prev = datetime.now()

if nbExpenseReport > 0 and 'expensereport' in enabledModule:
    ListExpenseReport = gen_random_following_date(yearToFill, nbExpenseReport, max_interval = dateinterval)
    
    for dateExpenseReport in tqdm(
        ListExpenseReport,
        desc="Création des notes de frais",
        unit="report"
    ):
        generate_expense_report(dateExpenseReport, testToggle)

start_stop = datetime.now()
duration = start_stop - start_prev
print("Alimentation notes de frais : ", duration)

# On affiche la durée de l'alimentation totale
print("Fin de l'alimentation à ", start_stop.strftime('%Y-%m-%d %H:%M:%S'))
# on affiche la durée
duration = start_stop - start_time
print("Durée totale de l'alimentation : ", duration)




"""
Refacto in progress

import datetime
from tqdm import tqdm
import traceback
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dolibarr_api import *
from generators import *
from utils import *
from generators.generators_config import GENERATORS

# On mémorise l'heure de début de l'alimentation totale
start_time = datetime.now()
print("Début de l'alimentation à ", start_time.strftime('%Y-%m-%d %H:%M:%S'))

# Affiche des messages de tests
if testing:
    testToggle = True
else :
    testToggle = False

# Récupération des modules actifs coté Dolibarr
enabledModule = get_enabled_modules()

for gen in GENERATORS:
    if gen["module"] not in enabledModule:
        print(f"⏭ Module {gen['module']} non activé — skip {gen['name']}")
        continue

    if gen["count"] <= 0:
        continue

    start_prev = datetime.datetime.now()

    try:
        dates = gen_random_following_date(
            yearToFill,
            gen["count"],
            max_interval=dateinterval
        )

        for date in tqdm(dates, desc=gen["progress_label"], unit="item"):
            gen["generator"](date, testToggle)

        duration = datetime.datetime.now() - start_prev
        print(f"✔ Alimentation {gen['name']} : {duration}")

    except Exception as e:
        print(f"❌ Erreur sur {gen['name']}: {e}")
        traceback.print_exc()

duration_total = datetime.datetime.now() - start_time
print("Fin de l'alimentation à ", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("Durée totale de l'alimentation : ", duration_total)


"""
