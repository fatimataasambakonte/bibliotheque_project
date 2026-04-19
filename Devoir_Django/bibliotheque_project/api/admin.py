from django.contrib import admin
from .models import Auteur, Livre

# Personnalisation du site admin existant (sans créer un nouveau)
admin.site.site_header = "Ma Bibliothèque"
admin.site.site_title = "Admin Bibliothèque"
admin.site.index_title = "Bienvenue sur l'admin"

@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nationalite', 'date_creation']
    search_fields = ['nom', 'nationalite']

@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'annee_publication', 'categorie', 'disponible']
    list_filter = ['categorie', 'disponible']
    search_fields = ['titre', 'isbn']