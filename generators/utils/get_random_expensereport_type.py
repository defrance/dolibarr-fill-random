import random

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from generators.utils.fill_expensereport_types import fill_expensereport_types

def get_random_expensereport_type(retDataExpensereportTypes):
    if (len(retDataExpensereportTypes) > 1):
        return retDataExpensereportTypes[random.randint(1, len(retDataExpensereportTypes)-1)]
    elif (len(retDataExpensereportTypes) == 1):
        return retDataExpensereportTypes[0]
    return 0

# Test unitaire
if __name__ == "__main__":
    retDataExpensereportTypes = fill_expensereport_types()
    print(get_random_expensereport_type(retDataExpensereportTypes))