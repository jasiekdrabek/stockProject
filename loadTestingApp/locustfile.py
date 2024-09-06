from locust import FastHttpUser ,HttpUser, task, constant, between, events
import random
import string
import faker
import psycopg2
import pytz
from datetime import datetime
import os
from gevent.lock import Semaphore

time=float(os.getenv("TIME_BETWEEN_REQUESTS"))
all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()

@events.spawning_complete.add_listener
def on_hatch_complete(**kw):
    all_locusts_spawned.release()


# Konfiguracja połączenia z bazą danych
conn = psycopg2.connect(
    dbname="test_stock",  # Nazwa bazy danych
    user="postgres",  # Użytkownik bazy danych
    password="postgres",  # Hasło do bazy danych
    host="db_test",  # Adres hosta (może być też 'db' jeśli baza działa w kontenerze Dockera)
    port="5432"  # Port, na którym działa PostgreSQL
)
cursor = conn.cursor()

# Inicjalizujemy generator danych
fake = faker.Faker()

def generate_random_data():
    username = fake.user_name()
    name = fake.first_name()
    surname = fake.last_name()
    email = fake.email()
    password = generate_valid_password()

    return {
        "username": username,
        "password": password,
        "name": name,
        "surname": surname,
        "email": email
    }

def generate_valid_password():
    password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))
    return password

class WebsiteReadOnlyUser(FastHttpUser):
    weight = 1
    wait_time = constant(time)
    token = ''
    
    def on_start(self):
        login = generate_random_data()
        self.client.post("/api/auth/signUp", json=login)
        data = {
            'username': login['username'],
            'password': login['password']
        }
        response = self.client.post("/api/auth/signIn",json=data)
        self.token = response.json()['token']
        company_name = fake.company()
        self.client.post("/api/company/addCompany",headers={"authorization": "Token " + self.token}, json={"name":company_name})
        all_locusts_spawned.wait()

    @task
    def getSellOffers(self):
        self.client.get("/api/user/sellOffers", headers={"authorization": "Token " + self.token})
        
    @task()
    def wait(self):
        pass
        
    @task
    def getBuyOffers(self):
        self.client.get("/api/user/buyOffers", headers={"authorization": "Token " + self.token})
        
    @task
    def getStocks(self):
        self.client.get("/api/user/stocks", headers={"authorization": "Token " + self.token})
        
    @task
    def getCompanies(self):
        self.client.get("/api/companies",headers={"authorization": "Token " + self.token})
        
class WebsiteActiveUser(HttpUser):
    weight = 2
    #wait_time = between(0.2, 0.5)
    wait_time = constant(time)
    token = ''
    
    def on_start(self):
        login = generate_random_data()
        self.client.post("/api/signUp", json=login)
        data = {
            'username': login['username'],
            'password': login['password']
        }
        response = self.client.post("/api/signIn",json=data)
        self.token = response.json()['token']
        company_name = fake.company()
        self.client.post("/api/addCompany",headers={"authorization": "Token " + self.token}, json={"name":company_name})
        all_locusts_spawned.wait()

    @task
    def wait(self):
        pass
    
    @task
    def addSellOffer(self):
        # Sprawdzenie, w jakich firmach użytkownik ma akcje
        response = self.client.get("/api/user/stocks", headers={"authorization": "Token " + self.token})
        user_stocks = response.json()
        if len(user_stocks) > 1:
            # Losowanie firmy, z której sprzedamy akcje
            stocks_to_choose_from = user_stocks[:-1]
            selected_stock = random.choice(stocks_to_choose_from)
            company_id = selected_stock['company']
            available_amount = selected_stock['amount']
            if available_amount == 0:
                return
            # Losowanie liczby akcji do sprzedaży (minimum 1, maksimum dostępne akcje)
            amount_to_sell = random.randint(1, min(available_amount,10))

            # Dodanie oferty sprzedaży
            sell_offer_data = {
                "company": company_id,
                "startAmount": amount_to_sell,
                "amount": amount_to_sell,
            }

            self.client.post("/api/addSellOffer", headers={"authorization": "Token " + self.token}, json=sell_offer_data)

    @task
    def addBuyOffer(self):
        # 1. Pobierz dane użytkownika, aby sprawdzić stan konta
        user_info_response = self.client.get("/api/user", headers={"authorization": "Token " + self.token})
        user_info = user_info_response.json()
        # 2. Sprawdź, czy użytkownik ma co najmniej 1000 jednostek waluty
        if user_info['moneyAfterTransations'] >= 1000:
            # 3. Pobierz listę firm dostępnych w systemie
            response = self.client.get("/api/companies", headers={"authorization": "Token " + self.token})
            companies = response.json()
            
            # 4. Wybierz losową firmę
            if len(companies) > 1:
                companies = companies[:-1]
                company = random.choice(companies)
                company_id = company['id']
                
                # 3. Określ losową liczbę akcji do zakupu i maksymalną cenę, jaką użytkownik jest gotów zapłacić
                amount = random.randint(1, 10)  # Losowa liczba akcji do zakupu
                
                # 4. Wyślij ofertę kupna
                buy_offer_data = {
                    "company": company_id,
                    "startAmount": amount,
                    "amount": amount,
                }
                self.client.post("/api/addBuyOffer", headers={"authorization": "Token " + self.token}, json=buy_offer_data)
           
    @events.request.add_listener
    def log_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
        try:
            if isinstance(response.json(), list):
                id = response.json()[-1]["request_id"]
            else:
                id = response.json()['request_id']
        except (ValueError, KeyError):
            # Jeśli nie można uzyskać request_id z odpowiedzi, użyj tymczasowego lub domyślnego
            id = 'unknown'
        local_tz = pytz.timezone('UTC')
        timestamp = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')

        # Zapisanie danych do modelu TrafficLog
        cursor.execute(
            """INSERT INTO "stockApp_trafficlog" (timestamp, request_id, api_time) VALUES (%s, %s, %s)""",
            (timestamp, id, response_time / 1000.0)  # Konwersja na sekundy
        )
        conn.commit()  # Zatwierdzenie transakcji
    