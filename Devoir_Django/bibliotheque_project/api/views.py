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
    return HttpResponse("""
    <html>
    <head>
        <title>Bibliothèque API</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: #f0f4f8; }
            h1 { color: #2c3e50; }
            p { color: #555; }
            .links { margin-top: 30px; }
            a { display: inline-block; margin: 10px; padding: 12px 25px;
                background: #3498db; color: white; text-decoration: none;
                border-radius: 8px; font-size: 16px; }
            a:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <h1>📚 Bienvenue dans ma Bibliothèque</h1>
        <p>API REST de gestion de livres et auteurs</p>
        <div class="links">
            <a href="/auteurs/">📖 Auteurs</a>
            <a href="/livres/">📕 Livres</a>
            <a href="/admin/">⚙️ Admin</a>
        </div>
    </body>
    </html>
    """)

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

class AuteurViewSet(viewsets.ModelViewSet):
    queryset = Auteur.objects.all()
    serializer_class = AuteurSerializer

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

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        qs = self.get_queryset().filter(disponible=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

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
        return Response({'message': f'Livre "{livre.titre}" emprunté avec succès.'})

    @action(detail=True, methods=['post'])
    def rendre(self, request, pk=None):
        livre = self.get_object()
        livre.disponible = True
        livre.save()
        return Response({'message': f'Livre "{livre.titre}" rendu avec succès.'})