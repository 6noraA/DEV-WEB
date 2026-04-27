from django import forms
from django.contrib.auth.models import User
from .models import Personne, Produit
from .models import Lieu
from .models import Information_locale
from .models import Signalement

class InscriptionForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

class PersonneForm(forms.ModelForm):
    class Meta:
        model = Personne
        fields = ['age', 'sexe', 'date_naissance', 'type_membre','photo']


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['ID', 'Nom', 'Connectiviter_type', 'etat', 'marque', 'mode', 'Bactterie', 'Adresse_IP', 'Temp_restante', 'Date_dernier_maintenance', 'Date_dernier_utilisation', 'Description', 'photo']

class LieuForm(forms.ModelForm):
    class Meta:
        model = Lieu
        fields = [
            'Nom',
            'Adresse',
            'Description',
            'latitude',
            'longitude',
            'photo',
            'liste_produits'
        ]

class InformationLocaleForm(forms.ModelForm):
    class Meta:
        model = Information_locale
        fields = [
            'nom',
            'description',
            'photo',
            'auteur'
        ]

class SignalementForm(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = [
            'nom',
            'description',
            'photo',
            'auteur'
        ]
