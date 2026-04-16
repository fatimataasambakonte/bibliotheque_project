# api/pagination.py
from rest_framework import viewsets
from .models import Livre
from .serializers import LivreSerializer
from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination
)
from rest_framework import viewsets
from .models import Livre
from .serializers import LivreSerializer

# ─── 1. PageNumberPagination ─────────────────────────────────────
# URL : /api/livres/?page=3
# Réponse : {count: 150, next: '...?page=4', previous: '...?page=2', results: [...]}
class StandardPagination(PageNumberPagination):
    page_size = 10 # éléments par défaut
    page_size_query_param = 'size' # ?size=20 pour surcharger
    max_page_size = 100 # maximum autorisé

# ─── 2. LimitOffsetPagination ────────────────────────────────────
# URL : /api/livres/?limit=10&offset=20 (livres 21 à 30)
class FlexiblePagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 50

# ─── 3. CursorPagination ─────────────────────────────────────────
# URL : /api/livres/?cursor=cD0yMDIz... (curseur opaque)
# Avantage : très performante pour grands datasets (pas de COUNT)
class PerformantePagination(CursorPagination):
    page_size = 10
    ordering = '-date_creation' # doit être un champ trié

# Utilisation dans un ViewSet :
class LivreViewSet(viewsets.ModelViewSet):
    queryset = Livre.objects.all()
    serializer_class = LivreSerializer
    pagination_class = StandardPagination # surcharge la pagination globale