from django import forms
from django.contrib.auth.models import User
from .models import BenutzerProfil, Projekt

class BenutzerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'email': 'E-Mail'
        }

class BenutzerProfilForm(forms.ModelForm):
    class Meta:
        model = BenutzerProfil
        fields = ['profil_bild']
        labels = {
            'profil_bild': 'Profilbild'
        }
