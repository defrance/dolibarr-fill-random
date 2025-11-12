from faker import Faker
import random
import string
import requests
import base64
import datetime
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

fake = Faker('fr_FR')

from dolibarr_api import *
from generators.generate_project import generate_project
from generators.generate_user import generate_user
from generators.generate_bank import generate_bank
from generators.generate_customer import generate_customer
from generators.generate_warehouse import generate_warehouse
from generators.generate_product import generate_product
from generators.generate_invoice import generate_invoice
from generators.generate_order import generate_order
from generators.generate_proposal import generate_proposal
from generators.generate_intervention import generate_intervention
from generators.generate_ticket import generate_ticket
from generators.generate_knowledge import generate_knowledge
from generators.generate_contract import generate_contract
from generators.generate_category import generate_category

from generators.utils.fill_users import fill_users
from generators.utils.fill_projects import fill_projects




# On mémorise l'heure de début de l'alimentation totale
start_time = datetime.now()
print("Début de l'alimentation à ", start_time.strftime('%Y-%m-%d %H:%M:%S'))

# Récupération des modules actifs coté Dolibarr
enabledModule = get_enabled_modules()
print ("Liste des modules activés dans Dolibarr")
print (enabledModule)

# Création des catégories
if newCategory > 0 and 'categorie' in enabledModule:
    for i in range(random.randint(1, newCategory)):
        generate_category("product")
    for i in range(random.randint(1, newCategory)):
        generate_category("customer")
    for i in range(random.randint(1, newCategory)):
        generate_category("contact")
    for i in range(random.randint(1, newCategory)):
        generate_category("ticket")

retDataCategProduct = fill_categories("product")
retDataCategCustomer = fill_categories("customer")
retDataCategContact = fill_categories("contact")

if 'ticket' in enabledModule:
    retDataCategTicket = fill_categories("ticket")

if nbNewWarehouse > 0 and 'stock' in enabledModule:
    listWareHouseGen = gen_random_following_date(yearToFill, nbNewWarehouse, max_interval = dateinterval)
    for dateCreate in listWareHouseGen:
        warehouse = generate_warehouse(dateCreate)

# On remplit les entrepots et les utilisateurs pour les alimentations aléatoires
retDataWarehouse = fill_warehouses()

if nbNewUser > 0:
    listUserGen = gen_random_following_date(yearToFill, nbNewUser, max_interval = dateinterval)
    for dateCreate in listUserGen:
        product = generate_user(dateCreate)

retDataUser = fill_users()

if nbNewBank > 0 and 'banque' in enabledModule:
    listBankGen = gen_random_following_date(yearToFill, nbNewBank, max_interval = dateinterval)
    for dateCreate in listBankGen:
        bank = generate_bank(dateCreate)

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
        client = generate_customer(dateCreate, retDataUser, retDataCategContact, retDataCategCustomer, enabledModule)

if nbNewProduct > 0:
    listProductGen = gen_random_following_date(yearToFill, nbNewProduct, max_interval = dateinterval)
    for dateCreate in listProductGen:
        product = generate_product(dateCreate, retDataWarehouse, retDataCategProduct, enabledModule)


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
        generate_project(dateProject,nbNewMaxTask, nbNewMaxTaskTime,nbNewMaxContact, retDataUser, retDataThirdParties)

retDataProjects = fill_projects()

start_stop = datetime.now()

duration = start_stop - start_prev
print("Durée Alimentation Projet et tâches : ", duration)

# ALimentation des factures
start_prev = datetime.now()

if nbNewBill > 0 and 'facture' in enabledModule:
    listFactureGen = gen_random_following_date(yearToFill, nbNewBill, max_interval = dateinterval)
    for dateFact in listFactureGen:
        facture = generate_invoice(dateFact, retDataPayment, retDataBank, retDataProduct, retDataThirdParties, retDataUser)

start_stop = datetime.now()
# on affiche la durée
duration = start_stop - start_prev
print("Durée Alimentation Factures et Règlement: ", duration)


# Alimentation des commandes et expéditions
start_prev = datetime.now()

if nbNewOrder > 0 and 'commande' in enabledModule:
    listOrderGen = gen_random_following_date(yearToFill, nbNewOrder, max_interval = dateinterval)
    for dateOrder in listOrderGen:
        commande = generate_order(dateOrder, retDataProduct, retDataThirdParties, retDataWarehouse, retDataUser)


start_stop = datetime.now()

# on affiche la durée
duration = start_stop - start_prev
print("Alimentation Commande et Expédition : ", duration)

# Alimentation des devis
start_prev = datetime.now()

if nbNewProposal > 0 and 'propal' in enabledModule:
    listProposalGen = gen_random_following_date(yearToFill, nbNewProposal, max_interval = dateinterval)
    for dateProposal in listProposalGen:
        propal = generate_proposal(dateProposal, retDataThirdParties, retDataProduct, retDataUser, retDataProjects)

start_stop = datetime.now()

# on affiche la durée
duration = start_stop - start_prev
print("Alimentation Devis : ", duration)

# Alimentation des contrats et interventions
start_prev = datetime.now()

if nbNewContract > 0 and 'contrat' in enabledModule:
    listContractGen = gen_random_following_date(yearToFill, nbNewContract, max_interval = dateinterval)
    for dateContract in listContractGen:
        contract = generate_contract(dateContract, retDataThirdParties, retDataProduct, retDataUser)

if nbNewFichinter > 0 and 'ficheinter' in enabledModule:
    listInterventionGen = gen_random_following_date(yearToFill, nbNewFichinter, max_interval = dateinterval)
    for dateInter in listInterventionGen:
        fichinter = generate_intervention(dateInter, retDataThirdParties, enabledModule)

start_stop = datetime.now()
# on affiche la durée de l'alimentation
duration = start_stop - start_prev
print("Durée Alimentation Contrat et intervention : ", duration)

# Alimentation des tickets et articles
start_prev = datetime.now()

if nbNewTicket > 0  and 'ticket' in enabledModule:
    listTicketGen = gen_random_following_date(yearToFill, nbNewTicket, max_interval = dateinterval)
    for dateTicket in listTicketGen:
        ticket = generate_ticket(dateTicket, retDataThirdParties, retDataUser)

if nbNewKnowledge > 0  and 'knowledgemanagement' in enabledModule:
    listArticleGen = gen_random_following_date(yearToFill, nbNewKnowledge, max_interval = dateinterval)
    for dateknowledge in listArticleGen:
        ticket = generate_knowledge(dateknowledge)

start_stop = datetime.now()
duration = start_stop - start_prev
print("Alimentation Tickets et articles : ", duration)

# On affiche la durée de l'alimentation totale
print("Fin de l'alimentation à ", start_stop.strftime('%Y-%m-%d %H:%M:%S'))
# on affiche la durée
duration = start_stop - start_time
print("Durée totale de l'alimentation : ", duration)