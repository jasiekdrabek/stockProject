import time
import docker
import psycopg2
import threading
import pytz
from datetime import datetime
import os

time.sleep(30)
# Konfiguracja połączenia z bazą danych
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port="5432"
)
cursor = conn.cursor()

# Połączenie z Dockerem
client = docker.from_env()

def calculate_cpu_percentage(stats):
    """
    Oblicza procentowe zużycie CPU na podstawie danych z Docker Stats.
    """
    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
    system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
    if system_delta > 0.0 and cpu_delta > 0.0:
        cpu_percentage = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
    else:
        cpu_percentage = 0.0
    return cpu_percentage

def log_container_usage(container):
    """
    Loguje zużycie zasobów CPU i pamięci dla pojedynczego kontenera.
    """
    local_tz = pytz.timezone('Europe/Warsaw')
    
    while True:
        timestamp = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')
        # Pobranie informacji o zasobach
        stats = container.stats(stream=False)
        cpu_percentage = calculate_cpu_percentage(stats)
        memory_usage = stats['memory_stats']['usage'] / (1024 * 1024)  # MB

        sql_insert = """
        INSERT INTO "stockApp_cpu" (timestamp, cpu_usage, memory_usage, contener_id)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (timestamp, cpu_percentage, memory_usage, container.name))
        conn.commit()

        time.sleep(2)  # Zapisuj dane co 5 sekund

def log_resource_usage():
    """
    Uruchamia wątki logowania zasobów dla każdego kontenera.
    """
    threads = []
    for container in client.containers.list():
        thread = threading.Thread(target=log_container_usage, args=(container,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    log_resource_usage()
