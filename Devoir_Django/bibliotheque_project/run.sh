#!/usr/bin/env bash
# run.sh — commande de démarrage du service Web

set -o errexit

# Render injecte le port d'écoute via la variable $PORT
# Remplacez 'monprojet' par le nom réel de votre projet Django
gunicorn monprojet.wsgi:application --bind 0.0.0.0:$PORT --workers 2