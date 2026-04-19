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
if User.objects.filter(username='admin').exists():
    User.objects.filter(username='admin').delete()
    print('Ancien admin supprimé')
User.objects.create_superuser('oumy', 'admin@example.com', '1234')
print('Superuser créé')
"