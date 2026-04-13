from django import form
from django.contrib.auth.models import User
from .models import Personne

class InscriptionForm(form.ModelForm):
    password = form.CharField(widget=form.PasswordInput)
  
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password']
      
class PersonneForm(form.ModelForm):
    class Meta:
        model = Personne
        fields = ['age', 'sexe', 'date_naissance', 'type_membre']
