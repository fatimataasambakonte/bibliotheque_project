# api/views.py

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Auteur, Livre
from .serializers import AuteurSerializer, LivreSerializer, LivreDetailSerializer
from .permissions import EstProprietaireOuReadOnly
from .filters import LivreFilter
from .pagination import StandardPagination
from django.http import HttpResponse

def home(request):
    return HttpResponse("Bienvenue dans ma bibliothèque")


# ==============================
# 🔹 APIView (manuel)
# ==============================

class AuteurListAPIView(generics.ListCreateAPIView):
    queryset = Auteur.objects.all()
    serializer_class = AuteurSerializer


class AuteurDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Auteur.objects.all()
    serializer_class = AuteurSerializer


class LivreListCreateView(generics.ListCreateAPIView):
    queryset = Livre.objects.all()
    serializer_class = LivreSerializer


class LivreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Livre.objects.all()
    serializer_class = LivreSerializer


# ==============================
# 🔹 ViewSet Auteur
# ==============================

class AuteurViewSet(viewsets.ModelViewSet):
    queryset = Auteur.objects.all()
    serializer_class = AuteurSerializer


# ==============================
# 🔹 ViewSet Livre (AVANCÉ)
# ==============================

class LivreViewSet(viewsets.ModelViewSet):
    queryset = (
        Livre.objects
        .select_related('auteur')
        .prefetch_related('tags')
        .all()
    )

    permission_classes = [EstProprietaireOuReadOnly]
    pagination_class = StandardPagination
    filterset_class = LivreFilter

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['titre', 'auteur__nom', 'isbn']
    ordering_fields = ['titre', 'annee_publication', 'date_creation']
    ordering = ['-date_creation']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LivreDetailSerializer
        return LivreSerializer

    def perform_create(self, serializer):
        serializer.save(cree_par=self.request.user)

    # 🔹 livres disponibles
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        qs = self.get_queryset().filter(disponible=True)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # 🔹 emprunter un livre
    @action(detail=True, methods=['post'])
    def emprunter(self, request, pk=None):
        livre = self.get_object()

        if not livre.disponible:
            return Response(
                {'erreur': "Ce livre n'est pas disponible."},
                status=status.HTTP_400_BAD_REQUEST
            )

        livre.disponible = False
        livre.save()

        return Response({
            'message': f'Livre "{livre.titre}" emprunté avec succès.'
        })

    # 🔹 rendre un livre
    @action(detail=True, methods=['post'])
    def rendre(self, request, pk=None):
        livre = self.get_object()

        livre.disponible = True
        livre.save()

        return Response({
            'message': f'Livre "{livre.titre}" rendu avec succès.'
        })