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