import random

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from generators.utils.fill_users import fill_users


def get_random_user_id(retDataUser):
	# on retourne les infos du produit
	return retDataUser[random.randint(1, len(retDataUser)-1)]


# Test unitaire
if __name__ == "__main__":
    retDataUser = fill_users(10)
    print(get_random_user_id(retDataUser))