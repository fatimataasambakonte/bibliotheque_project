#!/usr/bin/env bash
# build.sh — exécuté par Render lors de la construction

set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Appliquer les migrations
python manage.py migrate

python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(username='oumy')
u.is_staff = True
u.is_superuser = True
u.set_password('oumy2026')
u.save()
print('Superuser oumy mis à jour avec tous les droits')
"