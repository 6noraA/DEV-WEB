from django.shortcuts import render, redirect
from .form import ProduitForm, InscriptionForm, PersonneForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Produit, Personne

from django.contrib.auth import login, authenticate, logout

from django.core.mail import send_mail

@login_required
def creer_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_produits')
        else:
            print(form.errors)
    elif request.method == 'GET':
        form = ProduitForm()

    return render(request, 'produits/creer_produit.html', {'form': form})

def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'produits/liste_produits.html', {'produits': produits})

@login_required
def modifier_produit(request, id):
    produit = Produit.objects.get(ID=id)

    if request.method == "POST":
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
    else:
        form = ProduitForm(instance=produit)

    return render(request, "produits/modifier.html", {"form": form})

def detail_produit(request, id):
    produit = Produit.objects.get(ID=id)
    return render(request, 'produits/detail_produit.html', {'produit': produit})

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        personne_form = PersonneForm(request.POST)

        if form.is_valid() and personne_form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            profil = user.personne
            profil.age = personne_form.cleaned_data['age']
            profil.sexe = personne_form.cleaned_data['sexe']
            profil.date_naissance = personne_form.cleaned_data['date_naissance']
            profil.type_membre = personne_form.cleaned_data['type_membre']
            send_mail('Bienvenue', 'Votre compte a été créé', 'admin@ville.com', [user.email])
            profil.save()

            login(request, user)
            return redirect('accueil')

    else:
        form = InscriptionForm()
        personne_form = PersonneForm()

    return render(request, 'monapp/connexion.html', {
        'page_active': 'connexion',
        'form': form,
        'personne_form': personne_form,
    })

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

def reservation(request):
    return render(request, 'monapp/reservations.html', {'page_active': 'reservation'})

def vie_citoyenne(request):
    return render(request, 'monapp/vie_citoyenne.html', {'page_active': 'vie-citoyenne'})

def update_niveau(personne):
    if personne.points >= 7:
        personne.niveau = 'expert'
    elif personne.points >= 5:
        personne.niveau = 'avance'
    elif personne.points >= 3:
        personne.niveau = 'intermediaire'
    else:
        personne.niveau = 'debutant'

def connexion(request):
    error = None

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            personne = user.personne

            personne.nb_connexions += 1
            personne.points += 0.25

            update_niveau(personne)
            personne.save()
            return redirect('accueil')
        else:
            error = "Nom d'utilisateur ou mot de passe incorrect."

    return render(request, 'monapp/connexion.html', {'page_active': 'connexion', 'error': error})

def deconnexion(request):
    logout(request)
    return redirect('connexion')

@login_required
def profil(request):
    personne = request.user.personne
    return render(request, 'monapp/profil.html', {'personne': personne})

@login_required
def edit_profil(request):
    personne = request.user.personne
    user = request.user

    if request.method == 'POST':
        # Sauvegarde des champs Personne (age, sexe, photo, date_naissance, type_membre)
        form = PersonneForm(request.POST, request.FILES, instance=personne)
        if form.is_valid():
            form.save()

            # Sauvegarde des champs User (username, nom, prénom)
            nouveau_username = request.POST.get('username', '').strip()
            nouveau_nom      = request.POST.get('last_name', '').strip()
            nouveau_prenom   = request.POST.get('first_name', '').strip()

            if nouveau_username:
                user.username = nouveau_username
            user.last_name  = nouveau_nom
            user.first_name = nouveau_prenom
            user.save()

            messages.success(request, '✓ Votre profil a bien été mis à jour.')
            return redirect('profil')

    # Si GET ou formulaire invalide, on retourne sur le profil
    return redirect('profil')

@login_required
def liste_profils(request):
    personnes = Personne.objects.all()
    return render(request, 'liste_profils.html', {'personnes': personnes})

@login_required
def detail_profil(request, id):
    personne = Personne.objects.get(id=id)
    return render(request, 'detail_profil.html', {'personne': personne})