import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *

def get_random_address():
    fulladdress = fake.address()
    arrayaddress = fulladdress.split("\n")
    arraycpville = arrayaddress[1].split(" ")
    return arrayaddress[0], arraycpville[0], arraycpville[1]


if __name__ == "__main__":
    adresse, cp, ville = get_random_address()
    print("ville = ", ville)
    print("adresse : ", adresse)
    print("cp :", cp)