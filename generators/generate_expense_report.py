from faker import Faker
import random
import string
import requests
import base64
import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from generators.generate_utils import *
# from generators.utils.put_fk_project import put_fk_project

def generate_expense_report( dateStart, retDataUser, testing = False):
    url = urlBase + "expensereports"
    userID = get_random_user(retDataUser)['id']

    # Création de la note de frais par défaut en brouillon
    data = {
        "fk_user_author": userID, # par défaut on met l'admin
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
            urlReport = url + "/" + str(expenseReportID)
            if testing :
                print("Note de frais créée avec l'ID : ", expenseReportID)
                r = requests.get(urlReport, headers=headers)
                print("Détail de la note de frais :", r.json())

    except Exception as e:
        print("Erreur lors de la création du note de frais :", e)

    # Ajout des lignes de frais
    """
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
"""
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

    