# Użyj oficjalnego obrazu Python jako bazowy
FROM python:3.10-slim

# Ustawienie zmiennej środowiskowej, aby zapobiec błędowi „Input is not a tty”
ENV PYTHONUNBUFFERED 1

# Ustawienie katalogu roboczego
WORKDIR /app

# Skopiowanie pliku requirements.txt do katalogu roboczego
COPY requirements.txt /app/

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

# Skopiowanie całego projektu do katalogu roboczego
COPY . /app/

# Uruchomienie komendy collectstatic
#RUN python manage.py collectstatic --noinput

# Ustawienie domyślnej komendy do uruchomienia serwera Django
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "stockProject.wsgi:application"]
