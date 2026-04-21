from django import forms
from django.contrib.auth.models import User
from .models import Personne, Produit

class InscriptionForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password']
      
class PersonneForm(forms.ModelForm):
    class Meta:
        model = Personne
        fields = ['age', 'sexe', 'date_naissance', 'type_membre']

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['ID', 'Nom', 'Connectiviter_type', 'etat', 'marque', 'mode', 'Bactterie', 'Adresse_IP', 'Temp_restante', 'Date_dernier_maintenance', 'Date_dernier_utilisation', 'Description', 'photo']