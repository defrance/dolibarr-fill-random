# dolibarr-fill-random
Programme python créant de la data dans dolibarr via les api natives, le but étant d'avoir un jeu d'essai consistant pour réaliser des tests

En terme de performance, le programme met environ 30 minutes sur un macbook air M1 pour créer les éléments définis dans le fichier de paramétrage d'exemple. 

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
    - définition d'une durée pour les services et d'un poids pour les produits

- Devis
    - les devis peuvent ne pas être signées
    - les éléments antérieur à l'année en cours sont traité
    - les éléments de l'année en cours sont soit brouillon soit validé

- Commandes
    - les éléments antérieur à l'année en cours sont traité
    - les éléments de l'année en cours sont soit brouillon soit validé

- Expedition
    - associée a une commande
    - les éléments antérieur à l'année en cours sont traité
    - les éléments de l'année en cours sont soit brouillon soit validé

- Facture
    - les éléments antérieur à l'année en cours sont traité
    - les éléments de l'année en cours sont soit brouillon soit validé

- Contrat
    - soucis sur la création des ligne de contrat (warning)
    - on ouvre les services sur une période et on les fermes aussi

- Intervention
    - on rajoute le lien des interventions à des contrats
    - la ventilation sur les mois nécessite la Version 22 de dolibarr

- Ticket
    - la ventilation sur les mois nécessite la Version 22 de dolibarr

- Article (base de connaissance)
    - ajout de l'info sur ma widget de stat de dolibarr
    - nécessite la Version 22 de dolibarr pour la validation et l'annulation

- Categories (attention toute ne sont pas développé dans l'API)
    - produit
    - tiers
    - contact
- Ajout de contact Externe/interne
    - présent que sur devis, commande et facture

    https://github.com/Dolibarr/dolibarr/pull/34010
    
# Installation préalable
Le programme utilise faker pour générer des données aléatoire
Il utilise aussi yaml pour le fichier de paramétrage

il faut donc réaliser les commandes suivantes: 
pip install faker
pip install pyyaml

# PR réalisées sur le core de dolibarr pour activer certaines fonctions :
Si vous souhaitez utiliser le programme sur une version de dolibarr inférieur à la 22, il sera nécessaire de réaliser les correctifs suivants :
 
    - creation des lignes de contrats
    https://github.com/Dolibarr/dolibarr/pull/33938

    - Mise à jour des interventions (date d'opération)
    https://github.com/Dolibarr/dolibarr/pull/33835
    https://github.com/Dolibarr/dolibarr/pull/33836

    - Date de création transmise aux ticket
    https://github.com/Dolibarr/dolibarr/pull/33937

    - infos et modification sur la base de connaissance
    https://github.com/Dolibarr/dolibarr/pull/33960
    https://github.com/Dolibarr/dolibarr/pull/33962

    - date de création des expeditions ok 
    https://github.com/Dolibarr/dolibarr/pull/33995

    - Ajout de contact Externe/interne (récup du type de contact)
    https://github.com/Dolibarr/dolibarr/pull/34010
