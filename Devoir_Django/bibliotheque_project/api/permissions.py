from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny,
    BasePermission, SAFE_METHODS
)
from rest_framework import viewsets
from .models import Livre
from .serializers import LivreSerializer

# ─── Permission personnalisée ────────────────────────────────────────
class EstProprietaireOuReadOnly(BasePermission):
    """
    Règle : lecture libre, mais modification uniquement par le créateur.
    Le modèle doit avoir un champ 'cree_par' ForeignKey vers User.
    """
    message = 'Vous devez être le propriétaire pour modifier cet objet.'

    def has_permission(self, request, view):
        """Permission au niveau de la vue (avant d'accéder à un objet)"""
        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
        if request.method in SAFE_METHODS:
            return True  # Lecture autorisée à tous
        return request.user.is_authenticated  # Écriture : doit être connecté

    def has_object_permission(self, request, view, obj):
        """Permission au niveau de l'objet (après get_object())"""
        if request.method in SAFE_METHODS:
            return True  # Lecture toujours OK
        # Modification : uniquement le propriétaire ou un admin
        return obj.cree_par == request.user or request.user.is_staff


# ─── Utilisation dans une vue ─────────────────────────────────────
class LivreViewSet(viewsets.ModelViewSet):
    queryset = Livre.objects.all()
    serializer_class = LivreSerializer
    # Surcharge les permissions globales pour ce ViewSet
    permission_classes = [EstProprietaireOuReadOnly]

    # Permissions différentes selon l'action
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Enregistre automatiquement l'utilisateur connecté comme créateur
        serializer.save(cree_par=self.request.user)


# ─── Exemple d'utilisation des tokens (commentaires) ──────────────
# Étape 1 : Obtenir un token (POST avec identifiants)
# curl -X POST http://127.0.0.1:8000/api/auth/token/ \
#  -H 'Content-Type: application/json' \
#  -d '{"username": "admin", "password": "monpassword"}'

# Réponse :
# {
# "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
# "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
# }

# Étape 2 : Utiliser le token pour une requête protégée
# curl -X POST http://127.0.0.1:8000/api/livres/ \
#  -H 'Content-Type: application/json' \
#  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...' \
#  -d '{"titre": "L\'Étranger", "isbn": "9782070360024", ...}'

# Étape 3 : Rafraîchir le token expiré
# curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
#  -H 'Content-Type: application/json' \
#  -d '{"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."}'