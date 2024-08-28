import time
import psycopg2
import psutil
import threading
import pytz
from datetime import datetime
import os

# Konfiguracja połączenia z bazą danych
conn = psycopg2.connect(
    dbname="test_stock",  # Nazwa bazy danych
    user="postgres",  # Użytkownik bazy danych
    password="postgres",  # Hasło do bazy danych
    host="db_test",  # Adres hosta (może być też 'db' jeśli baza działa w kontenerze Dockera)
    port="5432"  # Port, na którym działa PostgreSQL
)
cursor = conn.cursor()

def log_cpu_usage():
    print("Starting CPU usage logging")
    time.sleep(60)
    id = os.getenv('ENV_ID')
    while True:
        print(id)
        local_tz = pytz.timezone('Europe/Warsaw')
        timestamp = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        sql_insert = """
        INSERT INTO "stockApp_cpu" (timestamp, cpu_usage, memory_usage,contener_id)
        VALUES (%s, %s, %s,%s)
        """

        # Wykonanie zapytania
        cursor.execute(sql_insert, (timestamp, cpu_usage, memory_usage,id))

        # Zatwierdzenie transakcji
        conn.commit()

        time.sleep(5)  # Zapisuj dane co 5 sekund

# Uruchomienie wątku do zbierania danych o CPU
threading.Thread(target=log_cpu_usage, daemon=True).start()