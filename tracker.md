
# Octobre 2025
## Tracker
### Semaine 1
|Lundi||20|
|---|---|---|
||||

|Mardi||21|
|---|---|---|
||||

|Mercredi||22|
|---|---|---|
||||

|Jeudi|23|
|---|---|
|dolibarr-fill-random|refacto pour generate = un fichier|
|dolibarr-fill-random| renommage pour uniformisation du code, generate au singulier ...|
|generate_bank| test unitaire|
|changelog.md|création|

|Vendredi|24|
|---|---|
|generate_project|randomisation des contacts interne attribués aux tâches, randomisation type de contact, mise en place test|
|generate_bank| ajout du params testing=False, et print si testing=True|
|generate_category|ajout du params testing=False, random_words pour le type en test et print si testing=True|
|generate_contract|ajout de params|
|generate_customer|ajout de params et de tests|
|generate_knowledge|ajout du testing=False et print si testing=True|
|dolibarr_fill_random| ajout des params pour les generates modifiés.|
|generate_warehouse| ajout du params testing=False, et print si testing=True|
|param.yml|ajout "new_max_contact:"|
|interface.py|création et test "hello world"|
|global|uniformisation de la nomenclature en cours|
....

## Todo
 - test unitaire
    - ~~generate_bank~~
    - ~~generate_category~~
    - generate_contract => probleme Tiers sur les tests (mauvaise fonction ou mauvaise nom de key probablement)
        - testing=True à mettre en place
    - ~~generate_customer => voir les fakeRetData
        - ligne 54 : pourquoi data est vide pour l'utilisateur référent ?
        - ~~testing=True print à mettre en place~~
        - erreur random 1 fois sur 3 
    - generate_intervention => probleme Tiers sur les tests (mauvaise fonction ou mauvaise nom de key probablement)
        - testing=True print à mettre en place
    - generate_invoice => retData tests
        - testing=True print à mettre en place
    - ~~generate_knowledge~~
    - generate_opportunity => pas implémenté
    - generate_order
    - generate_product
    - ~~generate_project~~
    - generate_proposal
    - generate_ticket
    - ~~generate_user~~
    - ~~generate_utils~~
    - ~~generate_warehouse~~

- interface

- generate_project
    - taches
        - date tache (s'affiche pas dans dolibarr, probablement devoir passer par un update)
            -possibilité que la tâche dépasse la date de fin du projet prévue si le projet est prévue comme dépassant le délai
        - Budget tache
        - statut
        - date de cloture
        - tag/catégories
    - pointages
        - ~~date pointage tache~~
        - ~~association contact pointage~~
        - ~~Tiers type~~
        - ~~email~~
        - % avancement réel
    - contact
        - association contact projet
            - type de contact
                - get_random_contact_type : brute => API dico des contacts
                    ~~=> probleme sur les sources externes ("socid" plutot de fk_people ?)~~ (c'etait bien la syntax)
        - ~~association contact tache~~
        
        - ~~tableau stock les contacts associés au projet **projectContacts**~~
        
    - update du temps réelle de la tache avec les temps des pointages
    - suivis des taches
    - facture le temps passé
    - ticket
    - random create_user
    - random update_user

- generate_opportunity

- generate_product
    - prix d'achat fournisseur
    - get_random_tva

- maj le param-sample.yml

- maj le readme

## Notes
 - pour 28/10
    - voir les dates des tâches
    - l'avancement des taches dans les pointages
    - statut des tâches