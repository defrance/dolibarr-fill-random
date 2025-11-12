import random

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.fill_projects import fill_projects

def get_random_project_id(retDataProjects):
	if (len(retDataProjects) > 1):
		return retDataProjects[random.randint(1, len(retDataProjects)-1)]['id']
	elif (len(retDataProjects) == 1):
		return retDataProjects[0]['id']
	return 0

# Test unitaire
if __name__ == "__main__":
    retDataProjects = fill_projects(10)
    print(get_random_project_id(retDataProjects))