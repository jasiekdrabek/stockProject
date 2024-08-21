import json
import time
from locust import HttpUser, task, between
import random
import string
import faker
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

import os
import django

# Ustawienie zmiennej środowiskowej z nazwą modułu ustawień
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockProject.settings')

# Inicjalizacja Django
django.setup()
# Inicjalizujemy generator danych
fake = faker.Faker()
token = ''

def generate_random_data():
    username = fake.user_name()
    name = fake.first_name()
    surname = fake.last_name()
    email = fake.email()
    password = generate_valid_password(username)

    return {
        "username": username,
        "password": password,
        "name": name,
        "surname": surname,
        "email": email
    }

def generate_valid_password(username):
    while True:
        # Generowanie losowego hasła
        password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))
        try:
            # Sprawdzamy czy hasło spełnia walidację Django
            authenticate(username=username, password=password)
            return password
        except ValidationError:
            continue

class WebsiteUser(HttpUser):
    wait_time = between(0.5, 1)

    @task(3)
    def wait(self):
        pass
    @task
    def newCompany(self):
        print(token)
        company_name = fake.company()
        self.client.post("/api/addCompany",headers={"authorization": "Token " + token}, json={"name":company_name})

    @task
    def getCompanies(self):
        print(token)
        self.client.get("/api/companies",headers={"authorization": "Token " + token})

    def on_start(self):
        login = generate_random_data()
        self.client.post("/api/signUp", json=login)
        time.sleep(1.0)
        data = {
            'username': login['username'],
            'password': login['password']
        }
        response = self.client.post("/api/signIn",json=data)
        global token
        token = response.json()['token']
        print(token)

