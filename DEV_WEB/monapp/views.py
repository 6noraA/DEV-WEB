from django.shortcuts import render, redirect
from .form import ProduitForm, InscriptionForm, PersonneForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Produit, Personne

from django.contrib.auth import login, authenticate, logout

from django.core.mail import send_mail


# ── Décorateur niveau requis ──────────────────────────────────────
def niveau_requis(*niveaux):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('connexion')
            try:
                personne = request.user.personne
                if personne.niveau not in niveaux:
                    messages.error(request, "⛔ Accès refusé. Niveau insuffisant.")
                    return redirect('accueil')
            except Exception:
                return redirect('accueil')
            return view_func(request, *args, **kwargs)
        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorator


# ── Produits ──────────────────────────────────────────────────────

@niveau_requis('avance', 'expert')
def creer_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Objet connecté ajouté avec succès.')
            return redirect('liste_produits')
        else:
            print(form.errors)
    else:
        form = ProduitForm()

    return render(request, 'produits/creer_produit.html', {'form': form})


def liste_produits(request):
    q      = request.GET.get('q', '').strip()
    etat   = request.GET.get('etat', '')
    marque = request.GET.get('marque', '')

    produits = Produit.objects.all()

    if q:
        produits = produits.filter(
            Q(Nom__icontains=q) | Q(Description__icontains=q)
        )
    if etat:
        produits = produits.filter(etat=etat)
    if marque:
        produits = produits.filter(marque__icontains=marque)

    etats   = Produit.objects.values_list('etat', flat=True).distinct()
    marques = Produit.objects.values_list('marque', flat=True).distinct()

    return render(request, 'produits/liste_produits.html', {
        'produits'           : produits,
        'etats'              : etats,
        'marques'            : marques,
        'q'                  : q,
        'etat_selectionne'   : etat,
        'marque_selectionnee': marque,
    })


@niveau_requis('avance', 'expert')
def modifier_produit(request, id):
    produit = Produit.objects.get(ID=id)

    if request.method == "POST":
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Objet modifié avec succès.')
            return redirect('detail_produit', id=produit.ID)
    else:
        form = ProduitForm(instance=produit)

    return render(request, "produits/modifier.html", {"form": form})


def detail_produit(request, id):
    produit = Produit.objects.get(ID=id)
    if request.user.is_authenticated:
        try:
            personne = request.user.personne
            personne.nb_actions += 1
            personne.points += 0.50
            update_niveau(personne)
            personne.save()
        except Exception:
            pass
    return render(request, 'produits/detail_produit.html', {'produit': produit})


# ── Inscription ───────────────────────────────────────────────────

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        personne_form = PersonneForm(request.POST)

        if form.is_valid() and personne_form.is_valid():
            # form.save() gère maintenant le hashage du mot de passe
            user = form.save()

            # Mise à jour du profil Personne créé automatiquement
            profil = user.personne
            profil.age = personne_form.cleaned_data['age']
            profil.sexe = personne_form.cleaned_data['sexe']
            profil.date_naissance = personne_form.cleaned_data['date_naissance']
            profil.type_membre = personne_form.cleaned_data['type_membre']
            profil.save()

            send_mail(
                'Bienvenue sur MaVille',
                'Votre compte a été créé avec succès.',
                'admin@ville.com',
                [user.email],
                fail_silently=True,  # évite un crash si le mail échoue
            )

            # Connexion automatique après inscription
            login(request, user)
            return redirect('accueil')

    else:
        form = InscriptionForm()
        personne_form = PersonneForm()

    return render(request, 'monapp/connexion.html', {
        'page_active'  : 'connexion',
        'form'         : form,
        'personne_form': personne_form,
    })


# ── Pages principales ─────────────────────────────────────────────

def accueil(request):
    q      = request.GET.get('q', '').strip()
    etat   = request.GET.get('etat', '')
    marque = request.GET.get('marque', '')

    produits = Produit.objects.all()

    if q:
        produits = produits.filter(
            Q(Nom__icontains=q) | Q(Description__icontains=q)
        )
    if etat:
        produits = produits.filter(etat=etat)
    if marque:
        produits = produits.filter(marque__icontains=marque)

    etats   = Produit.objects.values_list('etat', flat=True).distinct()
    marques = Produit.objects.values_list('marque', flat=True).distinct()

    return render(request, 'monapp/accueil.html', {
        'page_active'        : 'accueil',
        'produits'           : produits,
        'etats'              : etats,
        'marques'            : marques,
        'q'                  : q,
        'etat_selectionne'   : etat,
        'marque_selectionnee': marque,
    })

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


# ── Niveau ────────────────────────────────────────────────────────

def update_niveau(personne):
    if personne.points >= 7:
        personne.niveau = 'expert'
    elif personne.points >= 5:
        personne.niveau = 'avance'
    elif personne.points >= 3:
        personne.niveau = 'intermediaire'
    else:
        personne.niveau = 'debutant'


# ── Connexion / déconnexion ───────────────────────────────────────

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


# ── Profil ────────────────────────────────────────────────────────

@login_required
def profil(request):
    personne = request.user.personne
    autres_membres = Personne.objects.exclude(
        user=request.user
    ).select_related('user').order_by('-points')

    return render(request, 'monapp/profil.html', {
        'personne'      : personne,
        'autres_membres': autres_membres,
    })


@login_required
def edit_profil(request):
    personne = request.user.personne
    user = request.user

    if request.method == 'POST':
        form = PersonneForm(request.POST, request.FILES, instance=personne)
        if form.is_valid():
            form.save()

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

    return redirect('profil')


@login_required
def liste_profils(request):
    personnes = Personne.objects.all()
    return render(request, 'liste_profils.html', {'personnes': personnes})


@login_required
def detail_profil(request, id):
    personne = Personne.objects.get(id=id)
    return render(request, 'detail_profil.html', {'personne': personne})