import datetime
from tqdm import tqdm
import traceback
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dolibarr_api import *
from generators import *
from utils import *
from generators.generators_config import GENERATORS

# On mémorise l'heure de début de l'alimentation totale
start_time = datetime.now()
print("Début de l'alimentation à ", start_time.strftime('%Y-%m-%d %H:%M:%S'))

# Affiche des messages de tests
if testing:
    testToggle = True
else :
    testToggle = False

# Récupération des modules actifs coté Dolibarr
enabledModule = get_enabled_modules()

for gen in GENERATORS:
    if gen["module"] not in enabledModule:
        print(f"⏭ Module {gen['module']} non activé — skip {gen['name']}")
        continue

    if gen["count"] <= 0:
        continue

    start_prev = datetime.datetime.now()

    try:
        dates = gen_random_following_date(
            yearToFill,
            gen["count"],
            max_interval=dateinterval
        )

        for date in tqdm(dates, desc=gen["progress_label"], unit="item"):
            gen["generator"](date, testToggle)

        duration = datetime.datetime.now() - start_prev
        print(f"✔ Alimentation {gen['name']} : {duration}")

    except Exception as e:
        print(f"❌ Erreur sur {gen['name']}: {e}")
        traceback.print_exc()

duration_total = datetime.datetime.now() - start_time
print("Fin de l'alimentation à ", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("Durée totale de l'alimentation : ", duration_total)

