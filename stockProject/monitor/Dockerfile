FROM python:3.10-slim

# Ustawienie zmiennej środowiskowej, aby zapobiec błędowi „Input is not a tty”
ENV PYTHONUNBUFFERED 1

# Ustawienie katalogu roboczego
WORKDIR /app

# Skopiowanie pliku requirements.txt do katalogu roboczego
COPY requirements.txt /app/

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie skryptu do kontenera
COPY monitor.py /app/monitor.py

# Domyślne polecenie do uruchomienia skryptu
CMD ["python", "/app/monitor.py"]
