from django.shortcuts import render, redirect, get_object_or_404
from .form import ProduitForm, InscriptionForm, PersonneForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg

from .models import Produit, Personne

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User

from django.core.mail import send_mail

import json


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
            personne.save()
        except Exception:
            pass
    return render(request, 'produits/detail_produit.html', {'produit': produit})


# ── Statistiques ──────────────────────────────────────────────────

@niveau_requis('avance', 'expert')
def statistiques(request):
    """Dashboard statistiques des objets connectés — Module 3."""
    produits = Produit.objects.all()
    total    = produits.count()

    # ── Répartition par état ──
    etats_qs = produits.values('etat').annotate(count=Count('etat')).order_by('etat')
    etats_labels = [e['etat'] for e in etats_qs]
    etats_data   = [e['count'] for e in etats_qs]
    etats_colors = []
    color_map = {
        'ACTIF'       : '#22c55e',
        'INACTIF'     : '#94a3b8',
        'PANNE'       : '#ef4444',
        'MAINTENANCE' : '#f59e0b',
        'DECONNECTE'  : '#3b82f6',
    }
    for e in etats_labels:
        etats_colors.append(color_map.get(e, '#8b5cf6'))

    # ── Batterie par objet ──
    batterie_noms  = [p.Nom[:20] for p in produits]
    batterie_vals  = [p.Bactterie for p in produits]
    batterie_colors = []
    for b in batterie_vals:
        if b > 60:
            batterie_colors.append('#22c55e')
        elif b > 30:
            batterie_colors.append('#f59e0b')
        else:
            batterie_colors.append('#ef4444')

    # ── Répartition par marque ──
    marques_qs     = produits.values('marque').annotate(count=Count('marque')).order_by('-count')
    marques_labels = [m['marque'] for m in marques_qs]
    marques_data   = [m['count'] for m in marques_qs]

    # ── Répartition par mode ──
    modes_qs     = produits.values('mode').annotate(count=Count('mode'))
    modes_labels = [m['mode'] for m in modes_qs]
    modes_data   = [m['count'] for m in modes_qs]

    # ── Objets nécessitant attention ──
    objets_attention = produits.filter(etat__in=['PANNE', 'MAINTENANCE']).order_by('etat')

    # ── Objets batterie faible (< 30%) ──
    batterie_faible = produits.filter(Bactterie__lt=30).order_by('Bactterie')

    # ── Stats rapides ──
    nb_actifs      = produits.filter(etat='ACTIF').count()
    nb_pannes      = produits.filter(etat='PANNE').count()
    nb_maintenance = produits.filter(etat='MAINTENANCE').count()
    batt_moyenne   = produits.aggregate(avg=Avg('Bactterie'))['avg'] or 0

    return render(request, 'produits/statistiques.html', {
        'total'           : total,
        'nb_actifs'       : nb_actifs,
        'nb_pannes'       : nb_pannes,
        'nb_maintenance'  : nb_maintenance,
        'batt_moyenne'    : round(batt_moyenne, 1),
        # Graphiques (JSON)
        'etats_labels'    : json.dumps(etats_labels),
        'etats_data'      : json.dumps(etats_data),
        'etats_colors'    : json.dumps(etats_colors),
        'batterie_noms'   : json.dumps(batterie_noms),
        'batterie_vals'   : json.dumps(batterie_vals),
        'batterie_colors' : json.dumps(batterie_colors),
        'marques_labels'  : json.dumps(marques_labels),
        'marques_data'    : json.dumps(marques_data),
        'modes_labels'    : json.dumps(modes_labels),
        'modes_data'      : json.dumps(modes_data),
        # Listes
        'objets_attention': objets_attention,
        'batterie_faible' : batterie_faible,
    })


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


# ── Niveau ────────────────────────────────────────────────────────

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

    progression = {
        'debutant'     : ('intermediaire', 3),
        'intermediaire': ('avance', 5),
        'avance'       : ('expert', 7),
    }
    niveau_suivant   = None
    seuil_suivant    = None
    peut_monter      = False
    points_manquants = 0

    if personne.niveau in progression:
        niveau_suivant, seuil_suivant = progression[personne.niveau]
        peut_monter      = personne.points >= seuil_suivant
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
            messages.error(request, f"❌ Il vous manque {manque:.2f} pts pour passer au niveau suivant.")
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

    signalements = Signalement.objects.select_related('lieu')

    COULEURS = {
        "accident": "red",
        "danger": "orange",
        "autre": "blue"
    }

    for signalement in signalements:

        couleur = COULEURS.get(signalement.type_signalement, "gray")

        folium.Marker(
            location=[
                signalement.lieu.latitude,
                signalement.lieu.longitude
            ],
            popup=f"""
                <b>{signalement.nom}</b><br>
                Type: {signalement.get_type_signalement_display()}<br>
                Lieu: {signalement.lieu.Nom}<br>
                Objet concerné: {signalement.produit.Nom if signalement.produit else "Aucun"}
            """
            tooltip=signalement.nom,
            icon=folium.Icon(color=couleur)
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
            signalement = form.save(commit=False)

            #important : validation métier (clean)
            signalement.full_clean()
            signalement.save()

            return redirect('liste_signalements')

    else:
        form = SignalementForm()

    return render(request, 'signalements/creer_signalement.html', {
        'form': form
    })

def liste_signalements(request):
    type_filtre = request.GET.get('type')

    signalements = Signalement.objects.select_related('lieu', 'produit')

    if type_filtre:
        signalements = signalements.filter(type_signalement=type_filtre)

    return render(request, 'signalements/liste_signalements.html', {
        'signalements': signalements,
        'type_filtre': type_filtre
    })

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