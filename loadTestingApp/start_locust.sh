#!/bin/bash

# Opóźnienie przed uruchomieniem Locust
sleep 60

# Parametry testu
USERS=${LOCUST_USERS:-30}  # Domyślnie 10 użytkowników, jeśli zmienna nie jest ustawiona
SPAWN_RATE=${LOCUST_SPAWN_RATE:-1}  # Domyślna wartość dla ramp-up to 1 user/s
TIME=${LOCUST_TIME:-5m}  # Domyślny host, jeśli zmienna nie jest ustawiona
LOCUST_CLASS=${LOCUST_CLASS:-WebsiteActiveUser}  # Domyślna klasa użytkownika

# Uruchomienie Locust z podanymi parametrami
locust -f /app/locustfile.py --headless -u $USERS -r $SPAWN_RATE --host=http://web:8080 -t $TIME $LOCUST_CLASS