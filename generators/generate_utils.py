from faker import Faker
from datetime import datetime
from generators.utils.fill_projects import fill_projects

# Choisi la langue pour les fausses données de faker.
fake = Faker('fr_FR')

# récupération de l'année en cours
yearNow = datetime.now().year

def get_random_address():
    fulladdress = fake.address()
    arrayaddress = fulladdress.split("\n")
    arraycpville = arrayaddress[1].split(" ")
    return arrayaddress[0], arraycpville[0], arraycpville[1]

allProjects = fill_projects()

if __name__ == "__main__":
    adresse, cp, ville = get_random_address()
    print("ville = ", ville)
    print("adresse : ", adresse)
    print("cp :", cp)