import random

def get_realistic_qty_price(typefee_code):

    if typefee_code == "EX_KME":
        qty = random.randint(5, 300)  # kilomètres
        value_unit = round(random.uniform(0.30, 0.60), 2)

    elif typefee_code == "TF_LUNCH":
        qty = 1
        value_unit = round(random.uniform(12, 35), 2)

    elif typefee_code == "TF_TRIP":
        qty = 1
        value_unit = round(random.uniform(5, 250), 2)

    else:  # TF_OTHER
        qty = 1
        value_unit = round(random.uniform(5, 100), 2)

    return qty, value_unit
