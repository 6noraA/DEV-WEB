from django import forms
from django.contrib.auth.models import User
from .models import Personne, Produit
from .models import Lieu
from .models import Information_locale
from .models import Signalement


class InscriptionForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Mot de passe"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmer le mot de passe"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data

    def save(self, commit=True):
        # On ne sauvegarde PAS directement le mot de passe en clair
        user = super().save(commit=False)
        # On hache le mot de passe correctement
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class PersonneForm(forms.ModelForm):
    class Meta:
        model = Personne
        fields = ['age', 'sexe', 'date_naissance', 'type_membre', 'photo']


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
<<<<<<< HEAD
        fields = ['ID', 'Nom', 'Connectiviter_type', 'etat', 'marque', 'mode', 'Bactterie', 'Adresse_IP', 'Temp_restante', 'Date_dernier_maintenance', 'Date_dernier_utilisation', 'Description', 'photo']
=======
        fields = ['ID', 'Nom', 'Connectiviter_type', 'etat', 'marque', 'mode',
                  'Bactterie', 'Adresse_IP', 'Temp_restante', 'Date_dernier_maintenance',
                  'Date_dernier_utilisation', 'Description', 'photo']
from .models import Lieu, Information_locale, Signalement

>>>>>>> 9254315 (galère)

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
<<<<<<< HEAD
            'liste_produits'
        ]

=======
            'liste_produits',
        ]


>>>>>>> 9254315 (galère)
class InformationLocaleForm(forms.ModelForm):
    class Meta:
        model = Information_locale
        fields = [
            'nom',
            'description',
            'photo',
<<<<<<< HEAD
            'auteur'
        ]

=======
            'auteur',
        ]


>>>>>>> 9254315 (galère)
class SignalementForm(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = [
            'nom',
            'description',
            'photo',
            'auteur',
<<<<<<< HEAD
            'lieu',
            'type_signalement',
            'produit'
        ]
=======
            'type_signalement',
            'lieu',
            'produit',
        ]
>>>>>>> 9254315 (galère)
