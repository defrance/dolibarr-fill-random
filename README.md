# dolibarr-fill-random
Programme python créant de la data dans dolibarr via les api natives


## paramétrage 
le fichier param.yml contient le paramétrage du programme avec 3 parties :
- connection: les éléments pour se connecter via son api à dolibarr
- elements : le nombre d'éléments que l'on souhaite créer
- others: les paramètres annexes
  - year_to_fill : année de départ de création des éléments
  - date_interval : l'interval maximum entre deux dates

date_interval va conditionner le nombre moyen d'elements à créer mensuellement, avec 3 on a une quinzaine d'éléments par mois.
compter 180 element pour 1 ans de données, 420 sur 2 ans et demi...

## Elements créable par l'application

- Utilisateurs
    - Création des utilisateurs
- Tiers
    - possibilité de gérer plusieurs pays (ou on reste en france)
    - gestion des commerciaux affectés
- Contact 
    - Création aléatoire associé a un tiers 
- Entrepot
    - Création aléatoire
- Banque
    - Création aléatoire

- Produit et Service
    - Création d'un stock initial pour les produits dans l'un des entrepots
    - définition d'une durée pour les services

- Devis
    - les devis peuvent ne pas être signées
    - les éléments antérieur à l'année en cours sont traité
    - les éléments de l'année en cours sont soit brouillon soit validé
- Commandes
    - les éléments antérieur à l'année en cours sont traité
    - les éléments de l'année en cours sont soit brouillon soit validé
- Facture
    - les éléments antérieur à l'année en cours sont traité
    - les éléments de l'année en cours sont soit brouillon soit validé

- Intervention
    - la ventilation sur les mois nécessite la Version 22 de dolibarr