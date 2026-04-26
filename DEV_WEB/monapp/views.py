from django.shortcuts import render, redirect, get_object_or_404
from .form import ProduitForm, InscriptionForm, PersonneForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Produit, Personne

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User

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
        produits = produits.filter(Q(Nom__icontains=q) | Q(Description__icontains=q))
    if etat:
        produits = produits.filter(etat=etat)
    if marque:
        produits = produits.filter(marque__icontains=marque)
    etats   = Produit.objects.values_list('etat', flat=True).distinct()
    marques = Produit.objects.values_list('marque', flat=True).distinct()
    return render(request, 'produits/liste_produits.html', {
        'produits': produits, 'etats': etats, 'marques': marques,
        'q': q, 'etat_selectionne': etat, 'marque_selectionnee': marque,
    })


@niveau_requis('avance', 'expert')
def modifier_produit(request, id):
    produit = get_object_or_404(Produit, ID=id)
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
    produit = get_object_or_404(Produit, ID=id)
    if request.user.is_authenticated:
        try:
            personne = request.user.personne
            personne.nb_actions += 1
            personne.points += 0.50
            # PAS de update_niveau ici — le changement est manuel
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
            user = form.save()
            profil = user.personne
            profil.age = personne_form.cleaned_data['age']
            profil.sexe = personne_form.cleaned_data['sexe']
            profil.date_naissance = personne_form.cleaned_data['date_naissance']
            profil.type_membre = personne_form.cleaned_data['type_membre']
            profil.save()
            send_mail('Bienvenue sur MaVille', 'Votre compte a été créé avec succès.',
                      'admin@ville.com', [user.email], fail_silently=True)
            login(request, user)
            return redirect('accueil')
    else:
        form = InscriptionForm()
        personne_form = PersonneForm()
    return render(request, 'monapp/connexion.html', {
        'page_active': 'connexion', 'form': form, 'personne_form': personne_form,
    })


# ── Pages principales ─────────────────────────────────────────────

def accueil(request):
    q      = request.GET.get('q', '').strip()
    etat   = request.GET.get('etat', '')
    marque = request.GET.get('marque', '')
    produits = Produit.objects.all()
    if q:
        produits = produits.filter(Q(Nom__icontains=q) | Q(Description__icontains=q))
    if etat:
        produits = produits.filter(etat=etat)
    if marque:
        produits = produits.filter(marque__icontains=marque)
    etats   = Produit.objects.values_list('etat', flat=True).distinct()
    marques = Produit.objects.values_list('marque', flat=True).distinct()
    return render(request, 'monapp/accueil.html', {
        'page_active': 'accueil', 'produits': produits,
        'etats': etats, 'marques': marques,
        'q': q, 'etat_selectionne': etat, 'marque_selectionnee': marque,
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
            # On incrémente les points et connexions SANS changer le niveau automatiquement
            personne.nb_connexions += 1
            personne.points += 0.25
            personne.save()  # le niveau ne change pas ici
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

    # Calcul du niveau suivant et du seuil
    progression = {
        'debutant'     : ('intermediaire', 3),
        'intermediaire': ('avance', 5),
        'avance'       : ('expert', 7),
    }
    niveau_suivant = None
    seuil_suivant  = None
    peut_monter    = False
    points_manquants = 0

    if personne.niveau in progression:
        niveau_suivant, seuil_suivant = progression[personne.niveau]
        peut_monter = personne.points >= seuil_suivant
        points_manquants = max(0, seuil_suivant - personne.points)

    return render(request, 'monapp/profil.html', {
        'personne'        : personne,
        'autres_membres'  : autres_membres,
        'niveau_suivant'  : niveau_suivant,
        'seuil_suivant'   : seuil_suivant,
        'peut_monter'     : peut_monter,
        'points_manquants': points_manquants,
    })


@login_required
def changer_niveau(request):
    """Changement de niveau MANUEL — uniquement si l'utilisateur a assez de points."""
    if request.method == 'POST':
        personne = request.user.personne

        progression = {
            'debutant'     : ('intermediaire', 3),
            'intermediaire': ('avance', 5),
            'avance'       : ('expert', 7),
        }

        if personne.niveau == 'expert':
            messages.info(request, "🏆 Vous êtes déjà au niveau maximum !")
            return redirect('profil')

        niveau_suivant, seuil = progression[personne.niveau]

        if personne.points >= seuil:
            personne.niveau = niveau_suivant
            personne.save()
            labels = {
                'intermediaire': '⚡ Intermédiaire',
                'avance'       : '🔥 Avancé',
                'expert'       : '🏆 Expert',
            }
            messages.success(request, f"🎉 Félicitations ! Vous êtes maintenant {labels[niveau_suivant]} !")
        else:
            manque = seuil - personne.points
            messages.error(request, f"❌ Il vous faut {manque:.2f} pts pour passer au niveau suivant.")

    return redirect('profil')


@login_required
def voir_profil(request, user_id):
    user_cible = get_object_or_404(User, id=user_id)
    if user_cible == request.user:
        return redirect('profil')
    membre = get_object_or_404(Personne, user=user_cible)
    return render(request, 'monapp/profil_public.html', {'membre': membre})


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


# ── Administration ────────────────────────────────────────────────

@niveau_requis('expert')
def admin_dashboard(request):
    membres = Personne.objects.select_related('user').order_by('-points')
    return render(request, 'monapp/admin_dashboard.html', {
        'membres': membres, 'page_active': 'admin',
    })


@niveau_requis('expert')
def bannir_utilisateur(request, user_id):
    if request.method == 'POST':
        cible = get_object_or_404(User, id=user_id)
        if cible == request.user:
            messages.error(request, "Vous ne pouvez pas vous bannir vous-même.")
            return redirect('admin_dashboard')
        try:
            if cible.personne.niveau == 'expert':
                messages.error(request, "Impossible de bannir un autre expert.")
                return redirect('admin_dashboard')
        except Exception:
            pass
        raison = request.POST.get('raison', 'Violation des règles de la plateforme.')
        cible.is_active = False
        cible.save()
        if cible.email:
            send_mail(
                subject='⛔ Votre compte MaVille a été suspendu',
                message=f"Bonjour {cible.username},\n\nVotre compte a été suspendu.\nRaison : {raison}\n\n— L'équipe MaVille",
                from_email='admin@ville.com',
                recipient_list=[cible.email],
                fail_silently=True,
            )
        messages.success(request, f"✅ Le compte de {cible.username} a été suspendu.")
    return redirect('admin_dashboard')


@niveau_requis('expert')
def reactiver_utilisateur(request, user_id):
    if request.method == 'POST':
        cible = get_object_or_404(User, id=user_id)
        cible.is_active = True
        cible.save()
        if cible.email:
            send_mail(
                subject='✅ Votre compte MaVille a été réactivé',
                message=f"Bonjour {cible.username},\n\nVotre compte a été réactivé.\n\n— L'équipe MaVille",
                from_email='admin@ville.com',
                recipient_list=[cible.email],
                fail_silently=True,
            )
        messages.success(request, f"✅ Le compte de {cible.username} a été réactivé.")
    return redirect('admin_dashboard')


@niveau_requis('expert')
def supprimer_utilisateur(request, user_id):
    if request.method == 'POST':
        cible = get_object_or_404(User, id=user_id)
        if cible == request.user:
            messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
            return redirect('admin_dashboard')
        try:
            if cible.personne.niveau == 'expert':
                messages.error(request, "Impossible de supprimer un compte expert.")
                return redirect('admin_dashboard')
        except Exception:
            pass
        raison   = request.POST.get('raison', 'Décision administrative.')
        email    = cible.email
        username = cible.username
        cible.delete()
        if email:
            send_mail(
                subject='🗑️ Votre compte MaVille a été supprimé',
                message=f"Bonjour {username},\n\nVotre compte a été définitivement supprimé.\nRaison : {raison}\n\n— L'équipe MaVille",
                from_email='admin@ville.com',
                recipient_list=[email],
                fail_silently=True,
            )
        messages.success(request, f"✅ Le compte de {username} a été supprimé définitivement.")
    return redirect('admin_dashboard')