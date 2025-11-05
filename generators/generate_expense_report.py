from faker import Faker
import random
import string
import requests
import base64
import sys, os
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dolibarr_api import *
from generators.generate_utils import *
from utils.get_random.get_random_project import get_random_projectID

def generate_expense_report( dateStart, retDataUser, retDataProjects, testing = False):
    url = urlBase + "expensereports"
    
    #Choisi un projet aléatoire dont dépends la note de frais
    try:
        projectID = get_random_projectID(retDataProjects)
    
    except Exception as e:
        print("Erreur lors de la récupération d'un projet aléatoire :", e)
        projectID = 0

    # Choisi un utilisateur aléatoire du projet comme auteur de la note de frais
         
    # Création de la note de frais par défaut en brouillon
    data = {
        "fk_user_author": get_random_user(retDataUser)['id'], # par défaut on met l'admin
        "date_debut": dateStart.strftime('%Y-%m-%d'),
        "date_fin": fake.date_between_dates(dateStart, datetime.now()).strftime('%Y-%m-%d'),
        "note_public": fake.text(max_nb_chars=200),
        "note_private": fake.text(max_nb_chars=200),
        "fk_user_validator": get_random_user(retDataUser)['id'],
    }

    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code != 200:
            print('Erreur lors de la création du note de frais', r.status_code)
            print (r.text)
            return None
        else:
            expenseReportID = r.text
            if testing :
                print("Note de frais créée avec l'ID : ", expenseReportID)
                r = requests.get(urlBase + "expensereports/" + str(expenseReportID), headers=headers)
                print("Détail de la note de frais :", r.json())

    except Exception as e:
        print("Erreur lors de la création du note de frais :", e)

    # Ajout des lignes de frais
    dataLine = [
        {
        "comments": fake.text(max_nb_chars=100),
        "total_ht": "100.00000000",
        "total_tva": "20.00000000",
        "total_ttc": "120.00000000",
        "lines": null,
        "date_creation": null,
        "date_validation": null,
        "date_modification": null,
        "date_cloture": null,
        "user_author": null,
        "user_creation": null,
        "user_creation_id": null,
        "user_valid": null,
        "user_validation": null,
        "user_validation_id": null,
        "user_closing_id": null,
        "user_modification": null,
        "user_modification_id": null,
        "fk_user_creat": null,
        "fk_user_modif": null,
        "specimen": 0,
        "totalpaid": null,
        "extraparams": [],
        "product": null,
        "cond_reglement_supplier_id": null,
        "deposit_percent": null,
        "retained_warranty_fk_cond_reglement": null,
        "warehouse_id": null,
        "parent_element": "",
        "fk_parent_attribute": "",
        "rowid": "1",
        "fk_unit": null,
        "date_debut_prevue": null,
        "date_debut_reel": null,
        "date_fin_prevue": null,
        "date_fin_reel": null,
        "weight": null,
        "weight_units": null,
        "length": null,
        "length_units": null,
        "width": null,
        "width_units": null,
        "height": null,
        "height_units": null,
        "surface": null,
        "surface_units": null,
        "volume": null,
        "volume_units": null,
        "multilangs": null,
        "product_type": null,
        "fk_product": null,
        "desc": null,
        "description": null,
        "product_ref": null,
        "product_label": null,
        "product_barcode": null,
        "product_desc": null,
        "fk_product_type": null,
        "qty": "1",
        "duree": null,
        "remise_percent": null,
        "info_bits": null,
        "special_code": null,
        "subprice": null,
        "subprice_ttc": null,
        "tva_tx": "20.0000",
        "multicurrency_subprice": null,
        "multicurrency_subprice_ttc": null,
        "value_unit": "120.00000000",
        "date": "2025-11-02",
        "dates": 1762041600,
        "fk_c_type_fees": "2",
        "fk_c_exp_tax_cat": "0",
        "fk_expensereport": "1",
        "type_fees_code": "TF_TRIP",
        "type_fees_libelle": "Transportation",
        "type_fees_accountancy_code": null,
        "projet_ref": "PJ2510-0019",
        "projet_title": "Le confort d'atteindre vos buts en toute tranquilité",
        "rang": "0",
        "vatrate": "20.0000",
        "vat_src_code": "",
        "localtax1_tx": "0.0000",
        "localtax2_tx": "0.0000",
        "localtax1_type": "0",
        "localtax2_type": "0",
        "fk_ecm_files": null,
        "rule_warning_message": null
      }


    ]  

    # modification du statut de la note de frais
    # 0 = brouillon
    # 2 = validé en attente d'approbation
    # 5 = approuvé
        # date_approve:
    # 6 = payé
    # 99 = refusé
        # date_refuse:
       # detail_refuse: 
    






# testing

if __name__ == "__main__":
    print(
        generate_expense_report( 
            dateStart= fake.date_this_month(before_today=True),
            retDataUser =fill_users(), testing = True)
    )

"""
[
  {
    "module": null,
    "id": "1",
    "entity": "1",
    "import_key": null,
    "array_options": [],
    "array_languages": null,
    "contacts_ids": null,
    "contacts_ids_internal": null,
    "linkedObjectsIds": null,
    "canvas": null,
    "fk_project": null,
    "origin_type": null,
    "origin_id": null,
    "ref": "(PROV1)",
    "ref_ext": null,
    "status": 0,
    "region_id": null,
    "demand_reason_id": null,
    "transport_mode_id": null,
    "shipping_method": null,
    "fk_multicurrency": null,
    "multicurrency_code": null,
    "multicurrency_tx": null,
    "multicurrency_total_ht": null,
    "multicurrency_total_tva": null,
    "multicurrency_total_localtax1": null,
    "multicurrency_total_localtax2": null,
    "multicurrency_total_ttc": null,
    "last_main_doc": null,
    "fk_account": null,

    "total_ht": "100.00000000",
    "total_tva": "20.00000000",
    "total_localtax1": "0.00000000",
    "total_localtax2": "0.00000000",
    "total_ttc": "120.00000000",
    "lines": [
      {
        "module": null,
        "id": "1",
        "entity": null,
        "import_key": null,
        "array_options": [],
        "array_languages": null,
        "contacts_ids": null,
        "contacts_ids_internal": null,
        "linkedObjectsIds": null,
        "canvas": null,
        "origin_type": null,
        "origin_id": null,
        "ref": null,
        "ref_ext": null,
        "status": null,
        "region_id": null,
        "demand_reason_id": null,
        "transport_mode_id": null,
        "shipping_method": null,
        "multicurrency_tx": null,
        "multicurrency_total_ht": null,
        "multicurrency_total_tva": null,
        "multicurrency_total_localtax1": null,
        "multicurrency_total_localtax2": null,
        "multicurrency_total_ttc": null,
        "last_main_doc": null,
        "fk_account": null,
        "total_ht": "100.00000000",
        "total_tva": "20.00000000",
        "total_localtax1": "0.00000000",
        "total_localtax2": "0.00000000",
        "total_ttc": "120.00000000",
        "lines": null,
        "actiontypecode": null,
        "comments": "test",
        "civility_code": null,
        "date_creation": null,
        "date_validation": null,
        "date_modification": null,
        "tms": null,
        "date_cloture": null,
        "user_author": null,
        "user_creation": null,
        "user_creation_id": null,
        "user_valid": null,
        "user_validation": null,
        "user_validation_id": null,
        "user_closing_id": null,
        "user_modification": null,
        "user_modification_id": null,
        "fk_user_creat": null,
        "fk_user_modif": null,
        "specimen": 0,
        "totalpaid": null,
        "extraparams": [],
        "product": null,
        "cond_reglement_supplier_id": null,
        "deposit_percent": null,
        "retained_warranty_fk_cond_reglement": null,
        "warehouse_id": null,
        "parent_element": "",
        "fk_parent_attribute": "",
        "rowid": "1",
        "fk_unit": null,
        "date_debut_prevue": null,
        "date_debut_reel": null,
        "date_fin_prevue": null,
        "date_fin_reel": null,
        "weight": null,
        "weight_units": null,
        "length": null,
        "length_units": null,
        "width": null,
        "width_units": null,
        "height": null,
        "height_units": null,
        "surface": null,
        "surface_units": null,
        "volume": null,
        "volume_units": null,
        "multilangs": null,
        "product_type": null,
        "fk_product": null,
        "desc": null,
        "description": null,
        "product_ref": null,
        "product_label": null,
        "product_barcode": null,
        "product_desc": null,
        "fk_product_type": null,
        "qty": "1",
        "duree": null,
        "remise_percent": null,
        "info_bits": null,
        "special_code": null,
        "subprice": null,
        "subprice_ttc": null,
        "tva_tx": "20.0000",
        "multicurrency_subprice": null,
        "multicurrency_subprice_ttc": null,
        "value_unit": "120.00000000",
        "date": "2025-11-02",
        "dates": 1762041600,
        "fk_c_type_fees": "2",
        "fk_c_exp_tax_cat": "0",
        "fk_expensereport": "1",
        "type_fees_code": "TF_TRIP",
        "type_fees_libelle": "Transportation",
        "type_fees_accountancy_code": null,
        "projet_ref": "PJ2510-0019",
        "projet_title": "Le confort d'atteindre vos buts en toute tranquilité",
        "rang": "0",
        "vatrate": "20.0000",
        "vat_src_code": "",
        "localtax1_tx": "0.0000",
        "localtax2_tx": "0.0000",
        "localtax1_type": "0",
        "localtax2_type": "0",
        "fk_ecm_files": null,
        "rule_warning_message": null
      }
    ],
    "actiontypecode": null,
    "civility_code": null,
    "date_creation": null,
    "date_validation": null,
    "date_modification": null,
    "tms": null,
    "date_cloture": null,
    "user_author": null,
    "user_creation": null,
    "user_creation_id": null,
    "user_valid": null,
    "user_validation": null,
    "user_validation_id": null,
    "user_closing_id": null,
    "user_modification": null,
    "user_modification_id": null,
    "fk_user_creat": "1",
    "fk_user_modif": null,
    "specimen": 0,
    "totalpaid": null,
    "extraparams": [],
    "product": null,
    "cond_reglement_supplier_id": null,
    "deposit_percent": null,
    "retained_warranty_fk_cond_reglement": null,
    "warehouse_id": null,
    "line": null,
    "date_debut": 1762041600,
    "date_fin": 1762041600,
    "date_approbation": null,
    "fk_user": null,
    "user_approve_id": null,
    "modepaymentid": 0,
    "paid": "0",
    "user_paid_infos": null,
    "user_author_infos": "Daniel Joseph",
    "user_validator_infos": "",
    "rule_warning_message": null,
    "date_create": 1762166461,
    "fk_user_author": "91",
    "date_modif": 1762166801,
    "date_refuse": "",
    "detail_refuse": null,
    "fk_user_refuse": null,
    "date_cancel": "",
    "detail_cancel": null,
    "fk_user_cancel": null,
    "fk_user_validator": null,
    "datevalid": null,
    "date_valid": "",
    "fk_user_valid": null,
    "user_valid_infos": null,
    "date_approve": "",
    "fk_user_approve": null,
    "localtax1": "0.00000000",
    "localtax2": "0.00000000"
  }
]
"""