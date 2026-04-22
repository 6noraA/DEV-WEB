from django.shortcuts import render, redirect
from .form import ProduitForm, InscriptionForm, PersonneForm
from .models import Produit

from django.contrib.auth import login, authenticate, logout

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

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        personne_form = PersonneForm(request.POST)

        if form.is_valid() and personne_form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()

            profil = user.personne
            profil.age = personne_form.cleaned_data['age']
            profil.sexe = personne_form.cleaned_data['sexe']
            profil.date_naissance = personne_form.cleaned_data['date_naissance']
            profil.type_membre = personne_form.cleaned_data['type_membre']
            profil.save()

            return redirect('login')

    else:
        form = InscriptionForm()
        personne_form = PersonneForm()

    return render(request, 'inscription.html', {'form': form, 'personne_form': personne_form})

def accueil(request):
    return render(request, 'monapp/accueil.html', {'page_active': 'accueil'})

def transport(request):
    return render(request, 'monapp/transport.html', {'page_active': 'transport'})

def incident(request):
    return render(request, 'monapp/incident.html', {'page_active': 'incident'})

def services_public(request):
    return render(request, 'monapp/services_public.html', {'page_active': 'services-public'})

def info_locale(request):
    return render(request, 'monapp/info_locales.html', {'page_active': 'info-locale'})
def profil(request):
    return render(request, 'monapp/profil.html', {'page_active': 'profil'})

def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('accueil')

    return render(request, 'monapp/connexion.html', {'page_active': 'connexion'})

def deconnexion(request):
    logout(request)
    return redirect('login')

def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'produits/liste_produits.html', {'produits': produits})

def detail_produit(request, id):
    try:
        prod = Produit.objects.get(pk=id)
    except Produit.DoesNotExist:
        prod = None
    return render(request, 'produits/detail_produit.html', {'produit': prod})