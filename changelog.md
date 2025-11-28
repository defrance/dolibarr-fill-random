
# ChangeLog

## 2025-11 :

### Generators :

- **Catégories (category) :**
    - ajout de couleurs aléatoires

- **Projets (project) :**
    - ajout de contacts aux projets, tâches et pointages

- **Produits (product) :**
    - possibilité de choisir le nombre de prix de vente généré
    - possibilité de définir le pourcentage d'augmentation des prix pour les historiques (par défaut 10%)
    - ajout prix d'achats liés aux fournisseurs
    - possibilité de choisir le nombre max de fournisseurs par produit
    - possibilité de choisir le nombre max de prix d'achat par fournisseurs (pour historique)

- **Tickets (ticket) :**
    - association d'un projet du tier

- **Devis (proposal) :**
    - association d'un projet du tier

- **Factures (invoice) :**
    - association d'un projet du tier

- **Commandes (order) :**
    - association d'un projet du tier

- **Interventions (ficheinter/intervention) :**
    - association d'un projet du tier
    
### Params / Params-sample:

- **supplier** :
    - ajout de *' nb_supplier_product '* pour définir le nombre max de fournisseur par produit
    - ajout de *' nb_supplier_product_price '* pour définir le nombre max de prix d'achat par fournisseur d'un produit

- **project** :
    - ajout de *' new_max_contact '*
    - ajout de *' new_max_task_time '*
    - ajout de *' new_max_task '*

- **elements** :
    - ajout de *' nb_sale_price_history_max '*
    - ajout de *' pourcentage_aug_price_max '*

- **connection** :
    - ajout de *' lang '* pour choisir la langue des données générées
    - ajout de *'tests '* pour choisir l'affichage des prints de test


## 2025-10 :
- ajout des projets et des tâches
- découpage du generate
- ajout des pointages
- mise en place des testing unitaire
- unification des nommages   