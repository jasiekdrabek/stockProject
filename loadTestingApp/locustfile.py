import time
from locust import HttpUser, task, between, events
import random
import string
import faker
import psycopg2
import uuid
import psutil
import threading
import datetime


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
'''
class WebsiteReadOnlyUser(HttpUser):
    weight = 1
    wait_time = between(0.5, 1)
    token = ''

    @task(3)
    def wait(self):
        pass
    
    @task
    def getSellOffers(self):
        self.client.get("/api/user/sellOffers", headers={"authorization": "Token " + self.token})
        
    @task
    def getBuyOffers(self):
        self.client.get("/api/user/buyOffers", headers={"authorization": "Token " + self.token})
        
    @task
    def getStocks(self):
        self.client.get("/api/user/stocks", headers={"authorization": "Token " + self.token})
        
    @task
    def getCompanies(self):
        print(self.token)
        self.client.get("/api/companies",headers={"authorization": "Token " + self.token})

    def on_start(self):
        login = generate_random_data()
        self.client.post("/api/signUp", json=login)
        time.sleep(1.0)
        data = {
            'username': login['username'],
            'password': login['password']
        }
        response = self.client.post("/api/signIn",json=data)
        self.token = response.json()['token']
        company_name = fake.company()
        self.client.post("/api/addCompany",headers={"authorization": "Token " + self.token}, json={"name":company_name})
        '''
class WebsiteActiveUser(HttpUser):
    weight = 2
    wait_time = between(0.5, 1)
    token = ''
    
    def on_start(self):
        login = generate_random_data()
        self.client.post("/api/signUp", json=login)
        time.sleep(1.0)
        data = {
            'username': login['username'],
            'password': login['password']
        }
        response = self.client.post("/api/signIn",json=data)
        self.token = response.json()['token']
        company_name = fake.company()
        self.client.post("/api/addCompany",headers={"authorization": "Token " + self.token}, json={"name":company_name})

    @task
    def wait(self):
        pass
    
    @task
    def addSellOffer(self):
        # Sprawdzenie, w jakich firmach użytkownik ma akcje
        response = self.client.get("/api/user/stocks", headers={"authorization": "Token " + self.token})
        user_stocks = response.json()
        if user_stocks:
            # Losowanie firmy, z której sprzedamy akcje
            selected_stock = random.choice(user_stocks)
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
            if companies:
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
                start = datetime.datetime.now()
                self.client.post("/api/addBuyOffer", headers={"authorization": "Token " + self.token}, json=buy_offer_data)
                end = datetime.datetime.now()
                apiTime = end - start

    @events.request.add_listener
    def log_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
        request_id = str(uuid.uuid4())  # Unikalne ID dla żądania
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        # Zapisanie danych do modelu TrafficLog
        cursor.execute(
            """INSERT INTO "stockApp_trafficlog" (timestamp, request_id, api_time) VALUES (%s, %s, %s)""",
            (timestamp, request_id, response_time / 1000.0)  # Konwersja na sekundy
        )
        conn.commit()  # Zatwierdzenie transakcji

def log_cpu_usage():
    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        sql_insert = """
        INSERT INTO "stockApp_trafficcpu" (timestamp, cpu_usage, memory_usage)
        VALUES (%s, %s, %s)
        """

        # Wykonanie zapytania
        cursor.execute(sql_insert, (timestamp, cpu_usage, memory_usage))

        # Zatwierdzenie transakcji
        conn.commit()

        time.sleep(5)  # Zapisuj dane co 5 sekund

# Uruchomienie wątku do zbierania danych o CPU
threading.Thread(target=log_cpu_usage, daemon=True).start()
