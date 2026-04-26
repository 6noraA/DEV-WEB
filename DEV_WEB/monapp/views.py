from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .form import ProduitForm
from .models import Produit


from django.contrib.auth import login, authenticate, logout
from .forms import InscriptionForm, PersonneForm

from django.core.mail import send_mail

@login_required
def creer_produit(request):
    if request.method == 'POST' :
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
    produits =Produit.objects.all()
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

def detail_produit(request, produit_id):
    produit = Produit.objects.get(ID=produit_id)
    return render(request, 'produits/detail_produit.html', {'produit': produit})

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
            send_mail( 'Bienvenue', 'Votre compte a été créé','admin@ville.com',[user.email],)
            profil.save()

            return redirect('login')

    else:
        form = InscriptionForm()
        personne_form = PersonneForm()

    return render(request, 'inscription.html', {'form': form, 'personne_form': personne_form})


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
            return redirect('home')

    return render(request, 'connexion.html')


def deconnexion(request):
    logout(request)
    return redirect('login')
    
@login_required
def profil(request):
    personne = request.user.personne
    return render(request, 'profil.html',{'personne':personne})

@login_required
def edit_profil(request):
    personne = request.user.personne

    if request.method == 'POST':
        form = PersonneForm(request.POST, instance=personne)
        if form.is_valid():
            form.save()
            return redirect('profil')
    else:
        form = PersonneForm(instance=personne)

    return render(request, 'edit_profil.html', {'form': form})


    





