# api/serializers.py
from rest_framework import serializers
from .models import Auteur, Livre
from .models import Auteur, Livre, Tag  # Ajoute Tag ici

# ─── APPROCHE 1 : Serializer de base (déclaratif) ───────────────────────
# Chaque champ est déclaré manuellement → contrôle total
class AuteurSimpleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nom = serializers.CharField(max_length=200)
    nationalite = serializers.CharField(max_length=100, required=False)

    def create(self, validated_data):
        """Appelé par serializer.save() pour une CRÉATION"""
        return Auteur.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Appelé par serializer.save() pour une MISE À JOUR"""
        instance.nom = validated_data.get('nom', instance.nom)
        instance.nationalite = validated_data.get('nationalite', 
instance.nationalite)
        instance.save()
        return instance
    
# ─── APPROCHE 2 : ModelSerializer (recommandée) ─────────────────────────
# Génère automatiquement les champs depuis le modèle
class AuteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auteur # Modèle source
        fields = '__all__' # Tous les champs
        # OU : fields = ['id', 'nom', 'nationalite']
        # OU : exclude = ['biographie'] # Tous sauf biographie
        read_only_fields = ['id', 'date_creation'] # Non modifiables

class LivreSerializer(serializers.ModelSerializer):
    # Champ calculé (non stocké en BDD, lecture seule)
    auteur_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'isbn', 'annee_publication',
            'categorie', 'auteur', 'auteur_nom', 'disponible'
        ]
        read_only_fields = ['id']

    # Méthode pour le champ calculé : get_<nom_du_champ>
    def get_auteur_nom(self, obj):
        """obj = instance du Livre en cours de sérialisation"""
        return obj.auteur.nom
    
    # Validation d'un champ spécifique : validate_<nom_du_champ>
    def validate_isbn(self, value):
        """L'ISBN doit contenir exactement 13 chiffres"""
        # Enlever les tirets éventuels
        clean = value.replace('-', '')
        if not clean.isdigit() or len(clean) != 13:
            raise serializers.ValidationError(
                "L'ISBN doit contenir exactement 13 chiffres."
            )
        return value
    
    # Validation d'année
    def validate_annee_publication(self, value):
        """L'année doit être dans une plage raisonnable"""
        if value < 1000 or value > 2025:
            raise serializers.ValidationError(
                "L'année doit être entre 1000 et 2025."
            )
        return value
 
    # Validation globale (plusieurs champs ensemble)
    def validate(self, data):
        """Validation cross-champs"""
        # Exemple : les essais doivent avoir une biographie d'auteur
        if data.get('categorie') == 'essai':
            auteur = data.get('auteur')
            if auteur and not auteur.biographie:
                raise serializers.ValidationError(
                    "Les essais requièrent une biographie de l'auteur."
                )
        return data
    
# Serializer imbriqué : affiche les détails de l'auteur dans le livre
class LivreDetailSerializer(serializers.ModelSerializer):
    # Sérialiseur imbriqué en lecture (read_only=True)
    auteur = AuteurSerializer(read_only=True)
    # FK pour l'écriture (accepte un ID d'auteur)
    auteur_id = serializers.PrimaryKeyRelatedField(
        queryset=Auteur.objects.all(),
        source='auteur',
        write_only=True # N'apparaît pas dans la réponse
    )

    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'isbn', 'annee_publication',
            'categorie', 'auteur', 'auteur_id', 'disponible'
        ]

# Résultat GET /api/livres/1/ :
# {
# "id": 1,
# "titre": "Les Misérables",
# "auteur": {
# "id": 3,
# "nom": "Victor Hugo",
# "nationalite": "Française"
# },
# ...
# }

# Serializer pour Tag
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nom']

# Serializer complet pour Livre avec tags et auteur
class LivreCompletSerializer(serializers.ModelSerializer):
    """Sérialiseur avec gestion complète des relations"""

    # 1. Affichage simple : liste d'IDs
    # tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    # 2. Affichage avec noms : SlugRelatedField
    # tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='nom')

    # 3. Affichage complet imbriqué (lecture)
    tags = TagSerializer(many=True, read_only=True)

    # ForeignKey : affichage imbriqué en lecture
    auteur = AuteurSerializer(read_only=True)

    # FK : champ ID pour l'écriture
    auteur_id = serializers.PrimaryKeyRelatedField(
        queryset=Auteur.objects.all(),
        source='auteur',
        write_only=True
    )

    # ManyToMany : liste d'IDs pour l'écriture
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )

    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'isbn', 'annee_publication', 'categorie',
            'disponible', 'auteur', 'auteur_id', 'tags', 'tag_ids'
        ]

class AuteurAvecLivresSerializer(serializers.ModelSerializer):
    """
    Permet de créer un auteur ET ses livres en une seule requête POST.
    Exemple body :
    {
        "nom": "Albert Camus",
        "livres": [
            {"titre": "L'Étranger", "isbn": "9782070360024", "annee_publication": 1942},
            {"titre": "La Peste", "isbn": "9782070360030", "annee_publication": 1947}
        ]
    }
    """
    livres = LivreSerializer(many=True)  # pas read_only pour permettre l'écriture

    class Meta:
        model = Auteur
        fields = ['id', 'nom', 'nationalite', 'livres']

    def create(self, validated_data):
        # Extraire les données des livres imbriqués
        livres_data = validated_data.pop('livres', [])
        # Créer l'auteur
        auteur = Auteur.objects.create(**validated_data)
        # Créer chaque livre associé à cet auteur
        for livre_data in livres_data:
            Livre.objects.create(auteur=auteur, **livre_data)
        return auteur

    def update(self, instance, validated_data):
        livres_data = validated_data.pop('livres', [])
        # Mettre à jour l'auteur
        instance.nom = validated_data.get('nom', instance.nom)
        instance.nationalite = validated_data.get('nationalite', instance.nationalite)
        instance.save()
        # Stratégie : remplacer tous les livres existants
        instance.livres.all().delete()
        for livre_data in livres_data:
            Livre.objects.create(auteur=instance, **livre_data)
        return instance