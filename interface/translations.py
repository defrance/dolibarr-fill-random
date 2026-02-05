# Traductions des labels de l'interface

TRANSLATIONS = {
    "fr_FR": {
        # Elements
        "new_category": "Nouvelles catégories",
        "new_bank": "Nouveaux comptes bancaires",
        "new_bill": "Nouvelles factures clients",
        "new_client": "Nouveaux clients",
        "new_contract": "Nouveaux contrats",
        "new_fichinter": "Nouvelles fiches d'intervention",
        "new_knowledge": "Nouvelles bases de connaissances",
        "new_order": "Nouvelles commandes clients",
        "new_product": "Nouveaux produits",
        "new_proposal": "Nouveaux devis",
        "new_stock_movement": "Nouveaux mouvements de stock",
        "new_ticket": "Nouveaux tickets",
        "new_user": "Nouveaux utilisateurs",
        "new_user_group": "Nouveaux groupes d'utilisateurs",
        "new_warehouse": "Nouveaux entrepôts",
        "new_opportunity": "Nouvelles opportunités",
        "new_project": "Nouveaux projets",
        "new_supplier_bill": "Nouvelles factures fournisseurs",
        "new_supplier_order": "Nouvelles commandes fournisseurs",
        "new_holiday": "Nouveaux congés",
        "new_expense_report": "Nouvelles notes de frais",
        
        # Categories
        "new_category_customer": "Nouvelles catégories de clients",
        "new_category_product": "Nouvelles catégories de produits",
        "new_category_socpeople": "Nouvelles catégories de contacts",
        
        # Contacts
        "invoice_externe": "Contacts externes pour factures",
        "invoice_interne": "Contacts internes pour factures",
        "order_externe": "Contacts externes pour commandes",
        "order_interne": "Contacts internes pour commandes",
        "proposal_externe": "Contacts externes pour devis",
        "proposal_interne": "Contacts internes pour devis",
        
        # Others
        "date_interval": "Intervalle de dates (mois)",
        "nb_country": "Nombre de pays",
        "nb_shipping": "Nombre de méthodes d'expédition",
        "year_to_fill": "Année à remplir",
        "max_workers": "Nombre max de workers",
        "lang": "Langue",
        "fk_country": "ID pays par défaut",
        "tests": "Mode test",
        
        # Project
        "new_max_task": "Nombre max de tâches par projet",
        "new_max_task_time": "Nombre max de temps sur tâches",
        "new_max_contact": "Nombre max de contacts par projet",
        
        # Supplier
        "create_supplier": "Créer des fournisseurs",
        "nb_supplier_product": "Nombre de produits fournisseurs",
        "nb_supplier_product_price": "Nombre de prix fournisseurs",
        
        # HRM
        "nb_expense_report_line_max": "Lignes max par note de frais",
        "nb_holiday": "Nombre de congés",
        "nb_expense_report": "Nombre de notes de frais",
        
        # Products
        "nb_sale_price_history_max": "Historique max de prix de vente",
        "pourcentage_aug_price_max": "Pourcentage max d'augmentation prix",
        "nb_lot_by_product_max": "Lots max par produit",
    },
   #"en_US": {
        # Pour plus tard si besoin
    #   "new_client": "New customers",
    #   "new_product": "New products",
        # etc...
    #}
}

def get_translation(key, lang="fr_FR"):

    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]
    return key 