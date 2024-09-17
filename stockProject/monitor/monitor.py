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
    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
    system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
    if system_delta > 0.0 and cpu_delta > 0.0:
        cpu_percentage = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
    else:
        cpu_percentage = 0.0
    return cpu_percentage

def log_container_usage(container):    
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stats = container.stats(stream=False)
        cpu_percentage = calculate_cpu_percentage(stats)
        memory_usage = stats['memory_stats']['usage'] / (1024 * 1024)
        sql_insert = """
        INSERT INTO "stockApp_cpu" (timestamp, cpu_usage, memory_usage, contener_id)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (timestamp, cpu_percentage, memory_usage, container.name))
        conn.commit()
        time.sleep(2)

def log_resource_usage():
    threads = []
    for container in client.containers.list():
        thread = threading.Thread(target=log_container_usage, args=(container,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    log_resource_usage()
