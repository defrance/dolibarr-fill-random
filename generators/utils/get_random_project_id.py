import random

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from generate_utils import *

def get_random_project_id(retDataProject, socID = 'null', testing = False):
	if (len(retDataProject) > 1):
		return retDataProject[random.randint(1, len(retDataProject)-1)]['id']
	elif (len(retDataProject) == 1):
		return retDataProject[0]['id']
	return 0

# Test unitaire
if __name__ == "__main__":
    print(get_random_project_id(allProjects, testing = True))