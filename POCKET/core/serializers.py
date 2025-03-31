from rest_framework import serializers
from .models import Mitarbeiter, Projekt, Abrechnung, Reisebericht, Schulungskosten, Abordnung, ProjektMitarbeiter, Einnahme

class MitarbeiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mitarbeiter
        fields = '__all__'  # Tüm alanları JSON'a dönüştür

class ProjektSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projekt
        fields = '__all__'

class EinnahmeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Einnahme
        fields = '__all__'

class AbrechnungSerializer(serializers.ModelSerializer):
    class Meta:
        model = Abrechnung
        fields = '__all__'

class ReiseberichtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reisebericht
        fields = '__all__'

class SchulungskostenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schulungskosten
        fields = '__all__'

class AbordnungSerializer(serializers.ModelSerializer):
    class Meta:
        model = Abordnung
        fields = '__all__'

class ProjektMitarbeiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjektMitarbeiter
        fields = '__all__'
