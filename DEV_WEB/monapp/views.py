from django.shortcuts import render, redirect
from .form import ProduitForm, InscriptionForm, PersonneForm
from django.contrib.auth.decorators import login_required

from .models import Produit

from django.contrib.auth import login, authenticate, logout

from django.core.mail import send_mail

from .models import Lieu
from django.shortcuts import render, get_object_or_404
from .models import Lieu
from django.urls import reverse
from .models import Signalement
from .models import Information_locale
import folium
from django.contrib.staticfiles import finders

image_path = finders.find("images/image_fond.png")

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
           
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
 
           
            profil = user.personne
            profil.age = profil_form.cleaned_data['age']
            profil.sexe = profil_form.cleaned_data['sexe']
            profil.date_naissance = profil_form.cleaned_data['date_naissance']
            profil.type_membre = profil_form.cleaned_data['type_membre']
            send_mail( 'Bienvenue', 'Votre compte a été créé','admin@ville.com',[user.email],)
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
def profil(request):
    return render(request, 'monapp/profil.html', {'page_active': 'profil'})
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
            error = "Nom d'utilisateur ou mot de passe incorrect.

    return render(request, 'monapp/connexion.html', {'page_active': 'connexion', 'error': error})

def deconnexion(request):
    logout(request)
    return redirect('connexion')
    
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

@login_required
def liste_profils(request):
    personnes = Personne.objects.all()
    return render(request, 'liste_profils.html', {'personnes': personnes})

@login_required
def detail_profil(request, id):
    personne = Personne.objects.get(id=id)
    return render(request, 'detail_profil.html', {'personne': personne})

def detail_lieu(request, lieu_id):
    lieu = get_object_or_404(Lieu, id=lieu_id)

    produits = lieu.liste_produits.all()
    all_produits = Produit.objects.all()

    return render(request, 'lieux/detail_lieu.html', {
        'lieu': lieu,
        'produits': produits,
        'all_produits': all_produits
    })

def liste_lieux(request):
    lieux = Lieu.objects.all()
    return render(request, 'lieux/liste_lieux.html', {'lieux': lieux})

def creer_lieu(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        x = request.POST.get('x')
        y = request.POST.get('y')

        lieu = Lieu(nom=nom, x=x, y=y)
        lieu.save()

        return redirect('liste_lieux')

    return render(request, 'lieux/creer_lieu.html')

def carte_lieux(request):

    carte = folium.Map(
        location=[0, 0],
        zoom_start=2,
        tiles=None
    )

    # Fond de carte
    folium.raster_layers.ImageOverlay(
        image=image_path,
        bounds=[[-100, -100], [100, 100]],
        opacity=1
    ).add_to(carte)

   
    # Lieux base de données
    lieux_db = Lieu.objects.all()


    # Affichage lieux DB
    for lieu in lieux_db:
        folium.Marker(
            location=[lieu.y, lieu.x],
            popup=f"<b>{lieu.nom}</b>",
            tooltip=lieu.nom,
            icon=folium.Icon(color="blue")
        ).add_to(carte)

    return render(request, 'produits/carte.html', {
        'carte': carte._repr_html_()
    })

@login_required
def ajouter_produit_lieu(request, lieu_id, produit_id):
    lieu = get_object_or_404(Lieu, id=lieu_id)
    produit = get_object_or_404(Produit, ID=produit_id)

    lieu.liste_produits.add(produit)

    return redirect('detail_lieu', lieu_id=lieu.id)

@login_required
def retirer_produit_lieu(request, lieu_id, produit_id):
    lieu = get_object_or_404(Lieu, id=lieu_id)
    produit = get_object_or_404(Produit, ID=produit_id)

    lieu.liste_produits.remove(produit)

    return redirect('detail_lieu', lieu_id=lieu.id)

@login_required
def creer_signalement(request):
    if request.method == 'POST':
        form = SignalementForm(request.POST, request.FILES)
        if form.is_valid():
            signalement = form.save()
            return redirect('liste_signalements')
    return render(request, 'signalements/creer_signalement.html')

def liste_signalements(request):
    signalements = Signalement.objects.all()
    return render(request, 'signalements/liste_signalements.html', {'signalements': signalements})

@login_required
def creer_information_locale(request):
    if request.method == 'POST':
        form = InformationLocaleForm(request.POST, request.FILES)

        if form.is_valid():
            information_locale = form.save()
            return redirect('liste_informations_locales')

    return render(request, 'informations_locales/creer_information_locale.html')

def liste_informations_locales(request):
    informations_locales = Information_locale.objects.all()
    return render(request, 'informations_locales/liste_informations_locales.html', {'informations_locales': informations_locales})

def detail_information_locale(request, information_locale_id):
    information_locale = get_object_or_404(Information_locale, id=information_locale_id)
    return render(request, 'informations_locales/detail_information_locale.html', {'information_locale': information_locale})

def detail_signalement(request, signalement_id):
    signalement = get_object_or_404(Signalement, id=signalement_id)
    return render(request, 'signalements/detail_signalement.html', {'signalement': signalement})



    





