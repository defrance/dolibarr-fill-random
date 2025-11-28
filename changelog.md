
# ChangeLog

## 2025-11 :

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
    
    - ajout de *'tests '* pour choisir l'affichage des prints de test

- **autres**:
    - ajout de *' lang '* pour choisir la langue des données générées

## 2025-10 :

**Projets (projects)** :
    - création du générateur
    - association avec un Tiers
    - mise en place statut aléatoire (en cours, brouillon, terminé, validé)
    - dates de création, début, fin estimée et fin réelles cohérentes avec les status
    - mise en place aléatoire pour définir si un projet respecte la date limite, si il termine en avance ou en retard et gestion de la date de fin en conséquence
    - création d'un nombre aléatoire de tâches (entre 0 et le params défini) pour chaque projets
    - création d'un nombre aléatoire de pointage (entre 0 et le params défini)
    
**Fill-random** :
    - refactorisation : Création d'un dossier dédié aux generateurs. Un fichier par générateur.


