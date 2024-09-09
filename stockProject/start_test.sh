#!/bin/bash

# Ścieżka do pliku z parametrami
param_file="parametry.txt"

# Sprawdzenie, czy plik istnieje
if [ ! -f "$param_file" ]; then
  echo "Plik z parametrami $param_file nie istnieje!"
  exit 1
fi

# Inicjalizacja licznika
counter=1

# Iteracja przez każdy wiersz (zestaw parametrów) w pliku
while IFS= read -r params; do
  # Sprawdzenie, czy wiersz nie jest pusty
  if [[ -z "$params" ]]; then
    continue
  fi

  echo "Uruchamiam Dockera z parametrami: $params"

  # Uruchomienie Dockera za pomocą skryptu generate_docker-compose.sh z parametrami
  ./generate_docker-compose.sh $params

  # Czekaj
  echo "Oczekiwanie"
  #sleep 4200
   sleep 1500

  # Zatrzymanie kontenerów
  echo "Zatrzymuję kontenery..."
  docker-compose -f docker-compose.generated.yml down

  # Pobranie logów za pomocą skryptu get-logs.sh, z numerem iteracji w nazwie pliku
  echo "Pobieranie logów i zapisywanie do pliku: logdatabase_test$counter.sql"
  ./get_logs.sh "$counter"

  # Zwiększenie licznika
  counter=$((counter + 1))

  # Po zakończeniu iteracji dla tego zestawu parametrów
  echo "Zakończono przetwarzanie zestawu parametrów: $params"
done < "$param_file"

echo "Wszystkie testy zostały zakończone."