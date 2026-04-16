# api/filters.py
import django_filters
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Livre
from .serializers import LivreSerializer

class LivreFilter(django_filters.FilterSet):
    """
    Permet de filtrer les livres via des paramètres URL.
    Exemple : GET /api/livres/?categorie=roman&annee_min=1990&titre=misérables
    """
    # Filtre exact sur un champ
    categorie = django_filters.ChoiceFilter(choices=Livre.CATEGORIES)
    # Filtres de plage sur un entier
    annee_min = django_filters.NumberFilter(field_name='annee_publication', lookup_expr='gte')
    annee_max = django_filters.NumberFilter(field_name='annee_publication', lookup_expr='lte')
    # Filtre insensible à la casse (ILIKE en SQL)
    titre = django_filters.CharFilter(lookup_expr='icontains')
    # Filtre sur une relation (nom de l'auteur)
    auteur_nom = django_filters.CharFilter(field_name='auteur__nom', lookup_expr='icontains')
    # Filtre booléen
    disponible = django_filters.BooleanFilter()

    class Meta:
        model = Livre
        fields = ['categorie', 'disponible']

# Dans le ViewSet :
class LivreViewSet(viewsets.ModelViewSet):
    queryset = Livre.objects.all().select_related('auteur')
    serializer_class = LivreSerializer
    filterset_class = LivreFilter  # filtre avancé
    filter_backends = [
        DjangoFilterBackend,  # filtres personnalisés (LivreFilter)
        SearchFilter,         # ?search=mot_clé (cherche dans plusieurs champs)
        OrderingFilter,       # ?ordering=titre ou ?ordering=-annee_publication
    ]
    # SearchFilter cherche dans ces champs
    search_fields = ['titre', 'auteur__nom', 'isbn']
    # OrderingFilter autorise le tri sur ces champs
    ordering_fields = ['titre', 'annee_publication', 'date_creation']
    ordering = ['-date_creation']  # tri par défaut