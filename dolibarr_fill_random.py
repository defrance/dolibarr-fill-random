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

if nbNewGroup > 0 :
    for i in range(nbNewGroup):
        userGroup = generate_user_group(testToggle)

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
listFactureGen = [] 
if nbNewBill > 0 and 'facture' in enabledModule :
    listFactureGen = gen_random_following_date(yearToFill, nbNewBill, max_interval = dateinterval)

listOrderGen = [] 
if nbNewOrder > 0 and 'commande' in enabledModule:
    listOrderGen = gen_random_following_date(yearToFill, nbNewOrder, max_interval = dateinterval)

listProposalGen = [] 
if nbNewProposal > 0 and 'propal' in enabledModule:
    listProposalGen = gen_random_following_date(yearToFill, nbNewProposal, max_interval = dateinterval)

listContractGen = []
if nbNewContract > 0 and 'contrat' in enabledModule:
    listContractGen = gen_random_following_date(yearToFill, nbNewContract, max_interval = dateinterval)
 

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
    
    for dateContract in listContractGen:
        all_futures.append({
            'future': executor.submit(
                generate_contract,
                dateContract,
                retDataThirdParties,
                retDataProduct,
                retDataUser,
                testToggle
            ),
            'type': 'contrat'
        })

    # Compteurs pour le suivi
    completed = {'facture': 0, 'commande': 0, 'devis': 0, 'contrat': 0}
    total = {'facture': len(listFactureGen), 'commande': len(listOrderGen), 'devis': len(listProposalGen), 'contrat': len(listContractGen)}
    
    # Attendre la complétion avec barre de progression globale
    for item in tqdm(
        all_futures,
        desc="Création factures/commandes/devis/contrats",
        unit="doc"
    ):
        item['future'].result()
        completed[item['type']] += 1
    
    # Afficher les statistiques
    print(f"  → Factures: {completed['facture']}/{total['facture']}, "
          f"Commandes: {completed['commande']}/{total['commande']}, "
          f"Devis: {completed['devis']}/{total['devis']}, "
          f"Contrats: {completed['contrat']}/{total['contrat']}")

start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_prev
print("Durée Alimentation Factures, Commandes, Devis et contrat (en parallèle) : ", duration)

# Alimentation des interventions et tickets EN PARALLÈLE
start_prev = datetime.now()

# Préparer les listes de dates pour chaque type de génération
listInterventionGen = []
if nbNewFichinter > 0 and 'ficheinter' in enabledModule:
    listInterventionGen = gen_random_following_date(yearToFill, nbNewFichinter, max_interval = dateinterval)

listTicketGen = []
if nbNewTicket > 0 and 'ticket' in enabledModule:
    listTicketGen = gen_random_following_date(yearToFill, nbNewTicket, max_interval = dateinterval)

# Soumettre TOUTES les tâches (interventions, tickets) au pool en même temps
print(f"Utilisation de {max_workers} workers pour la parallélisation")
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    all_futures = []
    
    # Soumettre toutes les interventions
    for dateInter in listInterventionGen:
        all_futures.append({
            'future': executor.submit(
                generate_with_error_handling,
                generate_intervention,
                dateInter,
                retDataThirdParties,
                enabledModule,
                testToggle
            ),
            'type': 'intervention'
        })
    
    # Soumettre tous les tickets
    for dateTicket in listTicketGen:
        all_futures.append({
            'future': executor.submit(
                generate_with_error_handling,
                generate_ticket,
                dateTicket,
                retDataThirdParties,
                testToggle
            ),
            'type': 'ticket'
        })

    # Compteurs pour le suivi
    completed = {'intervention': 0, 'ticket': 0}
    total = {'intervention': len(listInterventionGen), 'ticket': len(listTicketGen)}
    
    # Attendre la complétion avec barre de progression globale
    for item in tqdm(
        all_futures,
        desc="Création interventions/tickets",
        unit="doc"
    ):
        item['future'].result()
        completed[item['type']] += 1
    
    # Afficher les statistiques
    print(f"  → Interventions: {completed['intervention']}/{total['intervention']}, "
          f"Tickets: {completed['ticket']}/{total['ticket']}")

start_stop = datetime.now()
duration = start_stop - start_prev
print("Durée Alimentation Interventions et Tickets (en parallèle) : ", duration)

# Alimentation des congés/absences et notes de frais EN PARALLÈLE
start_prev = datetime.now()

# Préparer les listes de dates pour chaque type de génération
listArticleGen = []
if nbNewKnowledge > 0 and 'knowledgemanagement' in enabledModule:
    listArticleGen = gen_random_following_date(yearToFill, nbNewKnowledge, max_interval = dateinterval)

listHolidayGen = []
if nbHoliday > 0 and 'holiday' in enabledModule:
    listHolidayGen = gen_random_following_date(yearToFill, nbHoliday, max_interval = dateinterval)

listExpenseReportGen = []
if nbExpenseReport > 0 and 'expensereport' in enabledModule:
    listExpenseReportGen = gen_random_following_date(yearToFill, nbExpenseReport, max_interval = dateinterval)

# Soumettre TOUTES les tâches (knowledge, congés, notes de frais) au pool en même temps
print(f"Utilisation de {max_workers} workers pour la parallélisation")
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    all_futures = []
    
    # Soumettre toutes les connaissances
    for dateknowledge in listArticleGen:
        all_futures.append({
            'future': executor.submit(
                generate_with_error_handling,
                generate_knowledge,
                dateknowledge,
                testToggle
            ),
            'type': 'knowledge'
        })
    
    # Soumettre tous les congés
    for dateHoliday in listHolidayGen:
        all_futures.append({
            'future': executor.submit(
                generate_with_error_handling,
                generate_holiday,
                dateHoliday,
                testToggle
            ),
            'type': 'holiday'
        })
    
    # Soumettre toutes les notes de frais
    for dateExpenseReport in listExpenseReportGen:
        all_futures.append({
            'future': executor.submit(
                generate_with_error_handling,
                generate_expense_report,
                dateExpenseReport,
                testToggle
            ),
            'type': 'expense'
        })

    # Compteurs pour le suivi
    completed = {'knowledge': 0, 'holiday': 0, 'expense': 0}
    total = {'Base connaissance': len(listArticleGen), 'Congés': len(listHolidayGen), 'note de frais': len(listExpenseReportGen)}
    
    # Attendre la complétion avec barre de progression globale
    for item in tqdm(
        all_futures,
        desc="Création knowledge/congés/notes de frais",
        unit="doc"
    ):
        item['future'].result()
        completed[item['type']] += 1
    
    # Afficher les statistiques
    print(f"  → Base connaissance: {completed['knowledge']}/{total['Base connaissance']}, "
          f"Congés: {completed['holiday']}/{total['Congés']}, "
          f"Notes de frais: {completed['expense']}/{total['note de frais']}")

start_stop = datetime.now()
duration = start_stop - start_prev
print("Durée Alimentation Knowledge, Congés et Notes de frais (en parallèle) : ", duration)

# On affiche la durée de l'alimentation totale
print("Fin de l'alimentation à ", start_stop.strftime('%Y-%m-%d %H:%M:%S'))
# on affiche la durée
duration = start_stop - start_time
print("Durée totale de l'alimentation : ", duration)
