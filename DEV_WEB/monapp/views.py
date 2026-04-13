from django.shortcuts import render, redirect
from .form import ProduitForm
from .models import Produit


from django.contrib.auth import login, authenticate, logout
from .forms import InscriptionForm, PersonneForm

def creer_produit(request):
    if request.method == 'POST' :
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    elif request.method == 'GET':
        form = ProduitForm()

    return render(request, 'produits/creer_produit.html', {'form': form})
# Create your views here.

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        personne_form = PersonneForm(request.POST)

        if form.is_valid() and personne_form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()

            profil = user.personne
            profil.age = profil_form.cleaned_data['age']
            profil.sexe = profil_form.cleaned_data['sexe']
            profil.date_naissance = profil_form.cleaned_data['date_naissance']
            profil.type_membre = profil_form.cleaned_data['type_membre']
            profil.save()

            return redirect('login')

    else:
        form = InscriptionForm()
        personne_form = PersonneForm()

    return render(request, 'inscription.html', {'form': form, 'personne_form': personne_form})


def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')

    return render(request, 'connexion.html')


def deconnexion(request):
    logout(request)
    return redirect('login')








