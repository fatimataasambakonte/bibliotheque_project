from django.contrib import admin
from .models import Auteur, Livre

class CustomAdminSite(admin.AdminSite):
    site_header = "Ma Bibliothèque"
    site_title = "Admin Bibliothèque"
    index_title = "Bienvenue sur l’admin"

    class Media:
        css = {
            'all': ('api/admin_custom.css',)
        }

admin.site = CustomAdminSite()

@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nationalite', 'date_creation']
    search_fields = ['nom', 'nationalite']

@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'annee_publication', 'categorie', 'disponible']
    list_filter = ['categorie', 'disponible']
    search_fields = ['titre', 'isbn']