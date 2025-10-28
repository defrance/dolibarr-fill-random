from faker import Faker
import random
import string
import requests
import base64
import datetime

fake = Faker('fr_FR')

print(fake.date_this_month().strftime("%Y-%m-%d %H:%M:%S"))