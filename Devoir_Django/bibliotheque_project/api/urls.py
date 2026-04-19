from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuteurListAPIView,
    AuteurDetailAPIView,
    LivreListCreateView,
    LivreDetailView,
    AuteurViewSet,
    LivreViewSet
)
from . import views

# Router pour ViewSets
router = DefaultRouter()
router.register(r'auteurs', AuteurViewSet, basename='auteur')
router.register(r'livres', LivreViewSet, basename='livre')

urlpatterns = [
    path('', views.home, name='home'),
    path('auteurs/', AuteurListAPIView.as_view(), name='auteur-list'),
    path('auteurs/<int:pk>/', AuteurDetailAPIView.as_view(), name='auteur-detail'),
    path('livres/', LivreListCreateView.as_view(), name='livre-list'),
    path('livres/<int:pk>/', LivreDetailView.as_view(), name='livre-detail'),
    path('', include(router.urls)),
]