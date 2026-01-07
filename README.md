# dolibarr-fill-random
Programme python créant de la data dans dolibarr via les api natives, le but étant d'avoir un jeu d'essai consistant pour réaliser des tests

En terme de performance, le programme met environ 1 heure sur un macbook air M1 (et la moitié sur un M4 ^^) pour créer les éléments définis dans le fichier de paramétrage d'exemple. 

## paramétrage 
le fichier param.yml contient le paramétrage du programme avec 3 parties :
- connection: les éléments pour se connecter via son api à dolibarr
- elements : le nombre d'éléments que l'on souhaite créer
- others: les paramètres annexes
  - year_to_fill : année de départ de création des éléments
  - date_interval : l'interval maximum entre deux dates

date_interval va conditionner le nombre moyen d'elements à créer mensuellement, avec 3 on a une quinzaine d'éléments par mois.
compter 180 element pour 1 ans de données, 450 sur 2 ans et demi...

## Paramétrage Dolibarr
il faut activer les modules et donner à l'utilisateur associé aux token les les droits sur celui-ci
Attention, l'utilisateur doit etre admin


## Elements créable par l'application

- Utilisateurs
    - Création des utilisateurs

- Tiers
    - possibilité de gérer plusieurs pays (sinon on reste en france)
    - gestion des commerciaux affectés
    - création des fournisseurs si activé

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

- Congés
	- 	Création aléatoire (en test)

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

- Projets / taches et temps saisies
   - la ventilation des taches sur les mois nécessite la Version 23 de dolibarr

# Installation préalable
Le programme utilise faker pour générer des données aléatoire
Il utilise aussi yaml pour le fichier de paramétrage

il faut donc réaliser les commandes suivantes: 
```
pip install faker

pip install pyyaml

pip install requests

pip install tqdm

python -m pip install --upgrade pip setuptools wheel

pip install kivy
```
# Tests unitaires
il n'y a pas à proprement parlé de tests unitaire mais chaque import à son propre lancement autonome

# PR réalisées sur le core de dolibarr pour activer certaines fonctions :
Si vous souhaitez utiliser le programme sur une version de dolibarr inférieur à la 22, il sera nécessaire de réaliser les correctifs suivants :

    - création des lignes de contrats
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
    - date de livraison mise à jour à la cloture au lieu de celle de l'éxpédition
    https://github.com/Dolibarr/dolibarr

    - Ajout de contact Externe/interne (récup du type de contact)
    https://github.com/Dolibarr/dolibarr/pull/34010

    - référencement et activation à distance de module (pas nécessaire pour le moment)
    https://github.com/Dolibarr/dolibarr/pull/34037
    
    - Ajout de la création des groupe d'utilisateurs
    https://github.com/Dolibarr/dolibarr/pull/34398

Si vous souhaitez utiliser le programme sur une version de dolibarr inférieur à la 23, il sera nécessaire de réaliser les correctifs suivants :

    - Gestion de la génération automatique de la référence des taches
    https://github.com/Dolibarr/dolibarr/pull/35981/files
	
    - Ajout de la date de création des taches dans la mises à jour
    https://github.com/Dolibarr/dolibarr/pull/36217
	
    - Gestion de la saisie des temps et des contacts sur les taches
    https://github.com/Dolibarr/dolibarr/pull/35897
	
    - Gestion des congés
    https://github.com/Dolibarr/dolibarr/pull/36606

Attention, nécéssite sur les versions antérieur à la V23 de modifier aussi le fichier /core/lib/functions2.lib.php getModuleDirForApiClass vers la ligne 2700
    il faut ajouter :
	
	 	} elseif ($moduleobject == 'holidays') {
			$moduledirforclass = 'holiday';
		}
