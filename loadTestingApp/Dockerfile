FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y dos2unix

# Skopiowanie pliku requirements.txt do katalogu roboczego
COPY requirements.txt /app/

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Kopiowanie skryptu startowego do kontenera
COPY start_locust.sh /app/start_locust.sh

# Ustawienie uprawnień do uruchomienia skryptu
RUN dos2unix /app/start_locust.sh && chmod +x /app/start_locust.sh

# Ustawienie domyślnej komendy startowej
#RUN /app/start_locust.sh
#CMD ["locust" "--host=http://192.168.1.110:8080"]
