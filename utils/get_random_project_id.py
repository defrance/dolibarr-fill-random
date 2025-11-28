import random

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from utils.get_projects_of_contactID import *
from utils.fill_projects import *


def get_random_project_id(retDataProject, testing = False):
	if (len(retDataProject) > 1):
		return retDataProject[random.randint(1, len(retDataProject)-1)]['id']
	elif (len(retDataProject) == 1):
		return retDataProject[0]['id']
	return 0

# Test unitaire
if __name__ == "__main__":
	print(get_random_project_id(fill_projects(), testing = True)) # a partir de la liste complète
	print(get_random_project_id(get_projects_of_contactID(574), testing = True)) # a partir de la liste d'un contact ayant des projets
	print(get_random_project_id(get_projects_of_contactID(1), testing = True)) # a partir de la liste d'un contact n'ayant pas de projet