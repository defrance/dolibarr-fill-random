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
    try:
        return generator_func(date, *args, **kwargs)
    except Exception as e:
        print(f"Erreur lors de la génération à la date {date}: {e}", flush=True)
        return None


def run_parallel_batch(futures_list, desc):
    """
    Exécute un batch de futures en parallèle, affiche une barre de progression
    et retourne un dict de compteurs {type: count}.
    """
    completed = {}
    total = {}
    for item in futures_list:
        t = item['type']
        completed.setdefault(t, 0)
        total.setdefault(t, 0)
        total[t] += 1

    # disable=False force tqdm même hors terminal (subprocess capturé)
    for item in tqdm(futures_list, desc=desc, unit="doc",
                     file=sys.stdout, disable=False, dynamic_ncols=True):
        item['future'].result()
        completed[item['type']] += 1

    stats = "  → " + ", ".join(
        f"{t.capitalize()}: {completed[t]}/{total[t]}"
        for t in total
    )
    print(stats, flush=True)
    return completed

# Début de l'alimentation

start_time = datetime.now()
print(f"Début de l'alimentation à {start_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

testToggle = bool(testing)

# Récupération des modules actifs côté Dolibarr
print("Récupération des modules actifs...", flush=True)
enabledModule = get_enabled_modules()
print(f"Modules activés : {enabledModule}", flush=True)

# Catégories

if newCategory > 0 and 'categorie' in enabledModule:
    print(f"Création de catégories (max {newCategory})...", flush=True)
    for i in range(random.randint(1, newCategory)):
        generate_category("product", testToggle)
    for i in range(random.randint(1, newCategory)):
        generate_category("customer", testToggle)
    for i in range(random.randint(1, newCategory)):
        generate_category("contact", testToggle)
    for i in range(random.randint(1, newCategory)):
        generate_category("ticket", testToggle)

print("Chargement des catégories...", flush=True)
retDataCategProduct  = fill_categories("product")
retDataCategCustomer = fill_categories("customer")
retDataCategContact  = fill_categories("contact")

if nbNewGroup > 0:
    print(f"Création de {nbNewGroup} groupe(s) utilisateur...", flush=True)
    for i in range(nbNewGroup):
        userGroup = generate_user_group(testToggle)

if 'ticket' in enabledModule:
    retDataCategTicket = fill_categories("ticket")

# Entrepôts, utilisateurs, banques

if nbNewWarehouse > 0 and 'stock' in enabledModule:
    print(f"Création de {nbNewWarehouse} entrepôt(s)...", flush=True)
    for dateCreate in gen_random_following_date(yearToFill, nbNewWarehouse, max_interval=dateinterval):
        generate_warehouse(dateCreate, testToggle)

retDataWarehouse = fill_warehouses()

if nbNewUser > 0:
    print(f"Création de {nbNewUser} utilisateur(s)...", flush=True)
    for dateCreate in gen_random_following_date(yearToFill, nbNewUser, max_interval=dateinterval):
        generate_user(dateCreate, testToggle)

retDataUser = fill_users()

if nbNewBank > 0 and 'banque' in enabledModule:
    print(f"Création de {nbNewBank} compte(s) bancaire(s)...", flush=True)
    for dateCreate in gen_random_following_date(yearToFill, nbNewBank, max_interval=dateinterval):
        generate_bank(dateCreate, testToggle)

if 'banque' in enabledModule:
    retDataBank    = fill_banks()
    retDataPayment = fill_payement_types()

print(f"Alimentation initiale terminée : {datetime.now() - start_time}", flush=True)
start_prev = datetime.now()

# Clients et produits

if nbNewClient > 0:
    print(f"Création de {nbNewClient} client(s)...", flush=True)
    for dateCreate in gen_random_following_date(yearToFill, nbNewClient, max_interval=dateinterval):
        generate_customer(dateCreate, retDataCategContact, retDataCategCustomer, enabledModule, testToggle)

if nbNewProduct > 0:
    print(f"Création de {nbNewProduct} produit(s)...", flush=True)
    for dateCreate in gen_random_following_date(yearToFill, nbNewProduct, max_interval=dateinterval):
        generate_product(dateCreate, retDataWarehouse, retDataCategProduct, enabledModule, testToggle)

retDataProduct      = fill_products()
retDataThirdParties = fill_thirdparties("customer")

if createSupplier == 1 and 'fournisseur' in enabledModule:
    retDataFournisseur = fill_thirdparties("supplier")

print(f"Durée Alimentation Tiers et produits : {datetime.now() - start_prev}", flush=True)

# Projets

start_prev = datetime.now()

if nbNewProject > 0 and 'projet' in enabledModule:
    print(f"Création de {nbNewProject} projet(s)...", flush=True)
    for dateProject in gen_random_following_date(yearToFill, nbNewProject, max_interval=dateinterval):
        generate_project(dateProject, nbNewMaxTask, nbNewMaxTaskTime, retDataUser, retDataThirdParties, testToggle)

retDataProjects = fill_projects()
print(f"Durée Alimentation Projets et tâches : {datetime.now() - start_prev}", flush=True)

# Factures, commandes, devis, contrats (parallèle)

start_prev = datetime.now()

listFactureGen  = gen_random_following_date(yearToFill, nbNewBill,     max_interval=dateinterval) if nbNewBill     > 0 and 'facture'  in enabledModule else []
listOrderGen    = gen_random_following_date(yearToFill, nbNewOrder,    max_interval=dateinterval) if nbNewOrder    > 0 and 'commande' in enabledModule else []
listProposalGen = gen_random_following_date(yearToFill, nbNewProposal, max_interval=dateinterval) if nbNewProposal > 0 and 'propal'   in enabledModule else []
listContractGen = gen_random_following_date(yearToFill, nbNewContract, max_interval=dateinterval) if nbNewContract > 0 and 'contrat'  in enabledModule else []

print(f"Utilisation de {max_workers} workers pour la parallélisation", flush=True)
print(f"  Factures: {len(listFactureGen)}, Commandes: {len(listOrderGen)}, Devis: {len(listProposalGen)}, Contrats: {len(listContractGen)}", flush=True)

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    all_futures = []

    for dateFact in listFactureGen:
        all_futures.append({'future': executor.submit(
            generate_with_error_handling, generate_invoice, dateFact,
            retDataPayment, retDataBank, retDataProduct, retDataThirdParties, retDataUser, testToggle
        ), 'type': 'facture'})

    for dateOrder in listOrderGen:
        all_futures.append({'future': executor.submit(
            generate_with_error_handling, generate_order, dateOrder,
            retDataProduct, retDataThirdParties, retDataWarehouse, retDataUser, testToggle
        ), 'type': 'commande'})

    for dateProposal in listProposalGen:
        all_futures.append({'future': executor.submit(
            generate_with_error_handling, generate_proposal, dateProposal,
            retDataThirdParties, retDataProduct, retDataUser, testToggle
        ), 'type': 'devis'})

    for dateContract in listContractGen:
        all_futures.append({'future': executor.submit(
            generate_contract, dateContract,
            retDataThirdParties, retDataProduct, retDataUser, testToggle
        ), 'type': 'contrat'})

    if all_futures:
        run_parallel_batch(all_futures, "Factures/Commandes/Devis/Contrats")

print(f"Durée Alimentation Factures, Commandes, Devis et Contrats : {datetime.now() - start_prev}", flush=True)

# Interventions et tickets (parallèle)

start_prev = datetime.now()

listInterventionGen = gen_random_following_date(yearToFill, nbNewFichinter, max_interval=dateinterval) if nbNewFichinter > 0 and 'ficheinter' in enabledModule else []
listTicketGen       = gen_random_following_date(yearToFill, nbNewTicket,    max_interval=dateinterval) if nbNewTicket    > 0 and 'ticket'     in enabledModule else []

print(f"Utilisation de {max_workers} workers pour la parallélisation", flush=True)
print(f"  Interventions: {len(listInterventionGen)}, Tickets: {len(listTicketGen)}", flush=True)

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    all_futures = []

    for dateInter in listInterventionGen:
        all_futures.append({'future': executor.submit(
            generate_with_error_handling, generate_intervention, dateInter,
            retDataThirdParties, enabledModule, testToggle
        ), 'type': 'intervention'})

    for dateTicket in listTicketGen:
        all_futures.append({'future': executor.submit(
            generate_with_error_handling, generate_ticket, dateTicket,
            retDataThirdParties, testToggle
        ), 'type': 'ticket'})

    if all_futures:
        run_parallel_batch(all_futures, "Interventions/Tickets")

print(f"Durée Alimentation Interventions et Tickets : {datetime.now() - start_prev}", flush=True)

# Knowledge, congés, notes de frais (parallèle)

start_prev = datetime.now()

listArticleGen       = gen_random_following_date(yearToFill, nbNewKnowledge, max_interval=dateinterval) if nbNewKnowledge  > 0 and 'knowledgemanagement' in enabledModule else []
listHolidayGen       = gen_random_following_date(yearToFill, nbHoliday,      max_interval=dateinterval) if nbHoliday       > 0 and 'holiday'             in enabledModule else []
listExpenseReportGen = gen_random_following_date(yearToFill, nbExpenseReport, max_interval=dateinterval) if nbExpenseReport > 0 and 'expensereport'       in enabledModule else []

print(f"Utilisation de {max_workers} workers pour la parallélisation", flush=True)
print(f"  Knowledge: {len(listArticleGen)}, Congés: {len(listHolidayGen)}, Notes de frais: {len(listExpenseReportGen)}", flush=True)

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    all_futures = []

    for dateknowledge in listArticleGen:
        all_futures.append({'future': executor.submit(
            generate_with_error_handling, generate_knowledge, dateknowledge, testToggle
        ), 'type': 'knowledge'})

    for dateHoliday in listHolidayGen:
        all_futures.append({'future': executor.submit(
            generate_with_error_handling, generate_holiday, dateHoliday, testToggle
        ), 'type': 'holiday'})

    for dateExpenseReport in listExpenseReportGen:
        all_futures.append({'future': executor.submit(
            generate_with_error_handling, generate_expense_report, dateExpenseReport, testToggle
        ), 'type': 'expense'})

    if all_futures:
        run_parallel_batch(all_futures, "Knowledge/Congés/Notes de frais")

print(f"Durée Alimentation Knowledge, Congés et Notes de frais : {datetime.now() - start_prev}", flush=True)

# TimeKeepr

start_prev = datetime.now()

if 'timekeepr' in enabledModule:
    print("Alimentation TimeKeepr...", flush=True)
    generate_timekeeper(
        nbMaxNewTimeSpentByTicket=nbMaxNewTimeSpentByTicket,
        nbMaxNewTimePlannedByTicket=nbMaxNewTimePlannedByTicket,
        NbMaxNewTimeSpentByIntervention=NbMaxNewTimeSpentByIntervention,
        nbMaxNewTimePlannedByIntervention=nbMaxNewTimePlannedByIntervention,
        testing=testToggle
    )

print(f"Durée Alimentation TimeKeepr : {datetime.now() - start_prev}", flush=True)

# Fin

end_time = datetime.now()
print(f"\nFin de l'alimentation à {end_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
print(f"Durée totale : {end_time - start_time}", flush=True)