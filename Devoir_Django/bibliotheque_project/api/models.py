# api/models.py
from django.db import models
from django.contrib.auth.models import User

class Auteur(models.Model):
    nom = models.CharField(max_length=200, verbose_name='Nom complet')

    biographie = models.TextField(blank=True, null=True, verbose_name='Biographie')

    nationalite = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Nationalité'
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
    
    class Meta:
        ordering = ['nom']
        verbose_name = 'Auteur'
        verbose_name_plural = 'Auteurs'


# ─── Modèle Tag ─────────────────────────────
class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom


# ─── Modèle Livre (fusion des deux) ─────────
class Livre(models.Model):

    CATEGORIES = [
        ('roman', 'Roman'),
        ('essai', 'Essai'),
        ('poesie', 'Poésie'),
        ('bd', 'Bande dessinée'),
        ('science', 'Science'),
        ('histoire', 'Histoire'),
    ]

    titre = models.CharField(max_length=300, verbose_name='Titre')

    isbn = models.CharField(
        max_length=17,
        unique=True,
        verbose_name='ISBN'
    )

    annee_publication = models.IntegerField(verbose_name='Année de publication')

    categorie = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        default='roman',
        verbose_name='Catégorie'
    )

    auteur = models.ForeignKey(
        Auteur,
        on_delete=models.CASCADE,
        related_name='livres',
        verbose_name='Auteur'
    )

    # ton code tags conservé
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='livres'
    )

    disponible = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titre} ({self.annee_publication})'
    
    class Meta:
        ordering = ['-annee_publication', 'titre']