from django.shortcuts import render, redirect, get_object_or_404
from .form import ProduitForm, InscriptionForm, PersonneForm, SignalementForm, InformationLocaleForm, LieuForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse

from .models import Produit, Personne, DemandePromotion

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User

from django.core.mail import send_mail
from .emails import (email_bienvenue, email_bannissement, email_reactivation,
    email_promotion_admin_acceptee, email_promotion_admin_refusee,
    email_demande_promotion_envoyee, email_confirmation_inscription,
    email_suppression, generer_token)

import json
import random


# ── Décorateur niveau requis ──────────────────────────────────────
def niveau_requis(*niveaux):
    """
    Niveaux : 'expert', 'administrateur'
    - 'expert'         : experts + administrateurs + superuser
    - 'administrateur' : administrateurs + superuser uniquement
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('connexion')
            try:
                personne = request.user.personne
                est_superuser = request.user.is_superuser
                est_admin     = est_superuser or personne.type_membre == 'administrateur'
                est_expert    = est_admin or personne.niveau == 'expert'

                if 'administrateur' in niveaux and not est_admin:
                    messages.error(request, "⛔ Accès refusé. Réservé aux administrateurs.")
                    return redirect('accueil')
                elif 'administrateur' not in niveaux and 'expert' in niveaux and not est_expert:
                    messages.error(request, "⛔ Accès refusé. Niveau expert requis.")
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


@login_required
def modifier_produit(request, id):
    produit  = get_object_or_404(Produit, ID=id)
    personne = request.user.personne
    est_admin  = request.user.is_superuser or personne.type_membre == 'administrateur'
    est_expert = est_admin or personne.niveau == 'expert'
    est_avance = est_expert or personne.niveau == 'avance'

    if not est_avance:
        messages.error(request, "Niveau avancé requis pour modifier un objet.")
        return redirect('detail_produit', id=produit.ID)

    # Formulaire sans le champ ID (clé primaire non modifiable)
    class ProduitModifierForm(ProduitForm):
        class Meta(ProduitForm.Meta):
            exclude = ['ID']

    if request.method == "POST":
        form = ProduitModifierForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            ajouter_points(request, points=0.5)
            messages.success(request, 'Objet modifié avec succès.')
            return redirect('detail_produit', id=produit.ID)
        else:
            print("Erreurs form:", form.errors)
    else:
        form = ProduitModifierForm(instance=produit)

    return render(request, "produits/modifier.html", {
        "form": form,
        "produit": produit,
    })


def detail_produit(request, id):
    produit = get_object_or_404(Produit, ID=id)
    ajouter_points(request, points=0.5)
    return render(request, 'produits/detail_produit.html', {'produit': produit})


# ── Simulation temps réel des objets connectés ────────────────────

def _simuler_tick(produits):
    """Simule l'évolution naturelle des objets connectés (température,
    batterie, état) à chaque appel. Persiste les changements en base."""
    for p in produits:
        if p.etat == 'PANNE':
            p.temperature = round(p.temperature + random.uniform(-0.3, 0.3), 1)
        elif p.etat == 'INACTIF' or p.etat == 'DECONNECTE':
            cible = 21.0
            p.temperature = round(p.temperature + (cible - p.temperature) * 0.1
                                  + random.uniform(-0.4, 0.4), 1)
        elif p.etat == 'MAINTENANCE':
            p.temperature = round(p.temperature + random.uniform(-1.0, 1.0), 1)
        else:  # ACTIF
            p.temperature = round(p.temperature + random.uniform(-1.5, 1.8), 1)

        # Bornes physiques réalistes
        if p.temperature < 5:   p.temperature = 5.0
        if p.temperature > 70:  p.temperature = 70.0

        # Décharge batterie selon l'état
        if p.etat == 'ACTIF':
            p.Bactterie = max(0, p.Bactterie - random.choice([0, 0, 1]))
        elif p.etat == 'MAINTENANCE':
            p.Bactterie = min(100, p.Bactterie + random.choice([0, 1, 2]))

        # Évolution probabiliste de l'état
        r = random.random()
        if p.Bactterie <= 3 and p.etat != 'INACTIF':
            p.etat = 'INACTIF'
        elif p.etat == 'ACTIF':
            if r < 0.02:   p.etat = 'MAINTENANCE'
            elif r < 0.025: p.etat = 'PANNE'
        elif p.etat == 'MAINTENANCE' and r < 0.15 and p.Bactterie > 30:
            p.etat = 'ACTIF'
        elif p.etat == 'PANNE' and r < 0.05:
            p.etat = 'MAINTENANCE'
        elif p.etat == 'INACTIF' and p.Bactterie > 20 and r < 0.10:
            p.etat = 'ACTIF'
        elif p.etat == 'DECONNECTE' and r < 0.08:
            p.etat = 'ACTIF'

        p.save(update_fields=['temperature', 'Bactterie', 'etat'])
    return produits


def api_produits_live(request):
    """Endpoint JSON consommé par la page d'accueil pour rafraîchir
    l'état des objets connectés en temps réel."""
    produits = list(Produit.objects.all())
    _simuler_tick(produits)
    data = [{
        'id'         : p.ID,
        'etat'       : p.etat,
        'temperature': p.temperature,
        'batterie'   : p.Bactterie,
        'mode'       : p.mode,
    } for p in produits]
    return JsonResponse({'produits': data})


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
    temp_moyenne   = produits.aggregate(avg=Avg('temperature'))['avg'] or 0

    return render(request, 'produits/statistiques.html', {
        'total'           : total,
        'nb_actifs'       : nb_actifs,
        'nb_pannes'       : nb_pannes,
        'nb_maintenance'  : nb_maintenance,
        'batt_moyenne'    : round(batt_moyenne, 1),
        'temp_moyenne'    : round(temp_moyenne, 1),
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
            # Compte inactif jusqu'a confirmation email
            user.is_active = False
            user.save()
            token = generer_token()
            personne = user.personne
            personne.token_confirmation = token
            personne.save()
            email_confirmation_inscription(user, token, request)
            messages.success(request, 'Compte cree ! Verifiez votre email pour activer votre compte.')
            return redirect('connexion')
    else:
        form = InscriptionForm()
        personne_form = PersonneForm()
    return render(request, 'monapp/connexion.html', {
        'page_active': 'connexion', 'form': form, 'personne_form': personne_form,
    })


# ── Système de points ────────────────────────────────────────────

def update_niveau(personne):
    if personne.points >= 7:
        personne.niveau = 'expert'
    elif personne.points >= 5:
        personne.niveau = 'avance'
    elif personne.points >= 3:
        personne.niveau = 'intermediaire'
    else:
        personne.niveau = 'debutant'


def ajouter_points(request, points, action=1):
    """Ajoute des points à l'utilisateur connecté et met à jour son niveau."""
    if not request.user.is_authenticated:
        return
    try:
        personne = request.user.personne
        personne.points    += points
        personne.nb_actions += action
        update_niveau(personne)
        personne.save()
    except Exception:
        pass


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

@login_required
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

def confirmer_email(request, token):
    from .models import Personne
    try:
        personne = Personne.objects.get(token_confirmation=token)
        personne.email_confirme = True
        personne.token_confirmation = None
        personne.user.is_active = True
        personne.user.save()
        personne.save()
        email_bienvenue(personne.user)
        messages.success(request, 'Email confirme ! Vous pouvez maintenant vous connecter.')
    except Personne.DoesNotExist:
        messages.error(request, 'Lien de confirmation invalide ou expire.')
    return redirect('connexion')


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

    # Demande de promotion en attente
    demande_en_attente = None
    if personne.niveau == 'expert' and personne.type_membre != 'administrateur':
        demande_en_attente = DemandePromotion.objects.filter(
            demandeur=personne, statut='en_attente'
        ).first()

    return render(request, 'monapp/profil.html', {
        'personne'          : personne,
        'autres_membres'    : autres_membres,
        'niveau_suivant'    : niveau_suivant,
        'seuil_suivant'     : seuil_suivant,
        'peut_monter'       : peut_monter,
        'points_manquants'  : points_manquants,
        'demande_en_attente': demande_en_attente,
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
    ajouter_points(request, points=0.25)
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

@niveau_requis('administrateur')
def admin_dashboard(request):
    membres = Personne.objects.select_related('user').order_by('-points')
    nb_demandes_en_attente = DemandePromotion.objects.filter(statut='en_attente').count()
    return render(request, 'monapp/admin_dashboard.html', {
        'membres': membres,
        'page_active': 'admin',
        'nb_demandes_en_attente': nb_demandes_en_attente,
    })


@niveau_requis('expert')
def bannir_utilisateur(request, user_id):
    if request.method == 'POST':
        cible = get_object_or_404(User, id=user_id)
        admin = request.user

        # Ne peut pas se bannir soi-même
        if cible == admin:
            messages.error(request, "Vous ne pouvez pas vous bannir vous-même.")
            return redirect('admin_dashboard')

        # Ne peut pas bannir un autre administrateur ou superuser
        try:
            est_admin_cible = (
                cible.is_superuser or
                cible.personne.type_membre == 'administrateur'
            )
            if est_admin_cible:
                messages.error(request, f"Impossible de bannir {cible.username} : il est administrateur.")
                return redirect('admin_dashboard')
        except Exception:
            pass

        raison = request.POST.get('raison', 'Violation des règles de la plateforme.')
        cible.is_active = False
        cible.save()
        email_bannissement(cible, raison)
        messages.success(request, f"Le compte de {cible.username} a été suspendu.")
    return redirect('admin_dashboard')


@niveau_requis('expert')
def reactiver_utilisateur(request, user_id):
    if request.method == 'POST':
        cible = get_object_or_404(User, id=user_id)
        cible.is_active = True
        cible.save()
        email_reactivation(cible)
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
        email_suppression(username, email, raison)
        cible.delete()
        messages.success(request, f"✅ Le compte de {username} a été supprimé définitivement.")
    return redirect('admin_dashboard')

# ── Lieux ─────────────────────────────────────────────────────────

from .models import Lieu
from .models import Signalement
from .models import Information_locale
import folium
import os
from django.conf import settings

# Chemin absolu vers l'image de fond — recherche dans tout le projet
import glob as _glob
_candidates = _glob.glob(str(settings.BASE_DIR) + '/**/carte.jpg', recursive=True)
image_path = _candidates[0] if _candidates else None


def detail_lieu(request, lieu_id):
    lieu = get_object_or_404(Lieu, id=lieu_id)
    produits = lieu.liste_produits.all()
    all_produits = Produit.objects.all()
    return render(request, 'lieux/detail_lieu.html', {
        'lieu': lieu,
        'produits': produits,
        'all_produits': all_produits,
    })


def liste_lieux(request):
    lieux = Lieu.objects.all()
    return render(request, 'lieux/liste_lieux.html', {'lieux': lieux})


@login_required
def creer_lieu(request):
    if request.method == 'POST':
        form = LieuForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Lieu ajouté avec succès.')
            return redirect('liste_lieux')
        else:
            print(form.errors)
    else:
        form = LieuForm()
    return render(request, 'lieux/creer_lieu.html', {'form': form})


def carte_lieux(request):
    carte = folium.Map(location=[0, 0], zoom_start=2, tiles=None)

    if image_path:
        folium.raster_layers.ImageOverlay(
            image=image_path,
            bounds=[[-100, -100], [100, 100]],
            opacity=1,
        ).add_to(carte)

    # ── Lieux (marqueurs bleus) ──
    lieux_db = Lieu.objects.all()
    for lieu in lieux_db:
        popup_html = (
            f"<b>{lieu.Nom}</b><br>"
            f"{lieu.Adresse}<br>"
            f"<a href='/lieux/{lieu.id}/'>Voir le détail</a>"
        )
        folium.Marker(
            location=[lieu.latitude, lieu.longitude],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=lieu.Nom,
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(carte)

    # ── Signalements (marqueurs colorés par type) ──
    COULEURS = {
        'accident': 'red',
        'danger':   'orange',
        'autre':    'blue',
    }
    signalements = Signalement.objects.select_related('lieu', 'produit').filter(lieu__isnull=False)
    for s in signalements:
        couleur = COULEURS.get(s.type_signalement, 'gray')
        popup_html = (
            f"<b>{s.nom}</b><br>"
            f"Type : {s.get_type_signalement_display()}<br>"
            f"Lieu : {s.lieu.Nom}<br>"
            f"Objet : {s.produit.Nom if s.produit else 'Aucun'}"
        )
        folium.Marker(
            location=[s.lieu.latitude, s.lieu.longitude],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=s.nom,
            icon=folium.Icon(color=couleur, icon='warning-sign'),
        ).add_to(carte)

    return render(request, 'produits/carte.html', {'carte': carte._repr_html_()})


@login_required
def ajouter_produit_lieu(request, lieu_id, produit_id):
    lieu    = get_object_or_404(Lieu, id=lieu_id)
    produit = get_object_or_404(Produit, ID=produit_id)
    lieu.liste_produits.add(produit)
    return redirect('detail_lieu', lieu_id=lieu.id)


@login_required
def retirer_produit_lieu(request, lieu_id, produit_id):
    lieu    = get_object_or_404(Lieu, id=lieu_id)
    produit = get_object_or_404(Produit, ID=produit_id)
    lieu.liste_produits.remove(produit)
    return redirect('detail_lieu', lieu_id=lieu.id)


# ── Signalements ──────────────────────────────────────────────────

@login_required
def creer_signalement(request):
    # Pré-remplissage depuis l'accueil (bouton "Signaler" sur un objet)
    produit_id  = request.GET.get('produit', '')
    produit_nom = request.GET.get('nom', '')

    if request.method == 'POST':
        form = SignalementForm(request.POST, request.FILES)
        if form.is_valid():
            signalement = form.save(commit=False)
            # Associe automatiquement l'utilisateur comme auteur
            if not signalement.auteur:
                signalement.auteur = request.user.username
            signalement.save()
            form.save_m2m()
            ajouter_points(request, points=1.0)
            messages.success(request, 'Signalement envoyé avec succès.')
            return redirect('liste_signalements')
    else:
        initial = {}
        if produit_id:
            try:
                produit_obj = Produit.objects.get(ID=produit_id)
                initial['produit'] = produit_obj
                initial['nom']     = f"Problème sur {produit_nom or produit_obj.Nom}"
            except Produit.DoesNotExist:
                pass
        form = SignalementForm(initial=initial)

    return render(request, 'signalements/creer_signalement.html', {
        'form': form,
        'produit_nom': produit_nom,
    })


def liste_signalements(request):
    signalements = Signalement.objects.all().order_by('-date')

    # Carte folium avec un marker par signalement
    # Les coordonnées sont dérivées de l'id pour les disperser sur la carte
    carte = folium.Map(location=[0, 0], zoom_start=2, tiles=None)
    if image_path:
        folium.raster_layers.ImageOverlay(
            image=image_path,
            bounds=[[-100, -100], [100, 100]],
            opacity=1,
        ).add_to(carte)

    # Positions prédéfinies dans la zone urbaine de la carte
    positions = [
        (18, 8), (-2, 12), (30, -5), (10, 25), (22, -18),
        (5, 0),  (35, 15), (-8, -5), (15, -12), (28, 5),
        (12, 18), (-5, 20), (40, 0), (8, -20), (20, 30),
    ]

    for i, sig in enumerate(signalements):
        # Utilise les coords du lieu si disponible, sinon position auto
        if sig.lieu:
            lat = sig.lieu.latitude
            lon = sig.lieu.longitude
            # Légère dispersion si plusieurs signalements au même lieu
            lat += (sig.id % 3) * 0.8
            lon += (sig.id % 4) * 0.8
        else:
            lat, lon = positions[i % len(positions)]
            lat += (sig.id % 5) * 1.5
            lon += (sig.id % 7) * 1.5

        COULEURS = {'accident': 'red', 'danger': 'orange', 'autre': 'blue'}
        couleur = COULEURS.get(sig.type_signalement, 'red')

        popup_html = (
            f"<b>⚠️ {sig.nom}</b><br>"
            f"Type : {sig.get_type_signalement_display()}<br>"
            f"Lieu : {sig.lieu.Nom if sig.lieu else 'Non précisé'}<br>"
            f"Objet : {sig.produit.Nom if sig.produit else 'Aucun'}<br>"
            f"<small>par {sig.auteur} — {sig.date}</small><br>"
            f"<a href='/signalements/{sig.id}/'>Voir le détail →</a>"
        )
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=sig.nom,
            icon=folium.Icon(color=couleur, icon="warning-sign"),
        ).add_to(carte)

    return render(request, 'signalements/liste_signalements.html', {
        'signalements': signalements,
        'carte': carte._repr_html_(),
    })


def detail_signalement(request, signalement_id):
    signalement = get_object_or_404(Signalement, id=signalement_id)
    return render(request, 'signalements/detail_signalement.html', {'signalement': signalement})


@login_required
def modifier_signalement(request, signalement_id):
    signalement = get_object_or_404(Signalement, id=signalement_id)
    personne    = request.user.personne
    est_admin   = request.user.is_superuser or personne.type_membre == 'administrateur'
    est_intermediaire = est_admin or personne.niveau in ['intermediaire', 'avance', 'expert']

    if not est_intermediaire:
        messages.error(request, "Niveau intermédiaire requis pour modifier un signalement.")
        return redirect('detail_signalement', signalement_id=signalement_id)

    if request.method == 'POST':
        form = SignalementForm(request.POST, request.FILES, instance=signalement)
        if form.is_valid():
            form.save()
            ajouter_points(request, points=0.5)
            messages.success(request, 'Signalement modifié avec succès.')
            return redirect('detail_signalement', signalement_id=signalement_id)
    else:
        form = SignalementForm(instance=signalement)

    return render(request, 'signalements/modifier_signalement.html', {
        'form': form,
        'signalement': signalement,
    })


# ── Informations locales ───────────────────────────────────────────

@login_required
def creer_information_locale(request):
    if request.method == 'POST':
        form = InformationLocaleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_informations_locales')
    else:
        form = InformationLocaleForm()
    return render(request, 'informations_locales/creer_information_locale.html', {'form': form})


def liste_informations_locales(request):
    informations_locales = Information_locale.objects.all()
    return render(request, 'informations_locales/liste_informations_locales.html', {
        'informations_locales': informations_locales,
    })


def detail_information_locale(request, information_locale_id):
    information_locale = get_object_or_404(Information_locale, id=information_locale_id)
    return render(request, 'informations_locales/detail_information_locale.html', {
        'information_locale': information_locale,
    })

# ── Demandes de promotion ─────────────────────────────────────────

@login_required
def demander_promotion(request):
    """Un expert peut demander à devenir administrateur."""
    personne = request.user.personne

    # Seuls les experts peuvent demander
    if personne.niveau != 'expert' and personne.type_membre != 'administrateur':
        messages.error(request, "⛔ Seuls les experts peuvent faire cette demande.")
        return redirect('profil')

    # Déjà admin
    if personne.type_membre == 'administrateur' or request.user.is_superuser:
        messages.info(request, "Vous êtes déjà administrateur.")
        return redirect('profil')

    # Demande déjà en attente
    if DemandePromotion.objects.filter(demandeur=personne, statut='en_attente').exists():
        messages.warning(request, "Vous avez déjà une demande en attente.")
        return redirect('profil')

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        DemandePromotion.objects.create(demandeur=personne, message=message)
        email_demande_promotion_envoyee(request.user)
        messages.success(request, "Votre demande a été envoyée aux administrateurs.")
        return redirect('profil')

    return render(request, 'monapp/demander_promotion.html')


@niveau_requis('administrateur')
def liste_demandes_promotion(request):
    """Les admins voient toutes les demandes en attente."""
    demandes = DemandePromotion.objects.filter(statut='en_attente').order_by('-date')
    return render(request, 'monapp/liste_demandes_promotion.html', {'demandes': demandes})


@niveau_requis('administrateur')
def traiter_demande_promotion(request, demande_id, action):
    """Accepter ou refuser une demande (action = 'accepter' ou 'refuser')."""
    demande = get_object_or_404(DemandePromotion, id=demande_id)
    admin   = request.user.personne

    if action == 'accepter':
        demande.statut = 'acceptee'
        demande.demandeur.type_membre = 'administrateur'
        demande.demandeur.niveau      = 'expert'
        demande.demandeur.save()
        email_promotion_admin_acceptee(demande.demandeur.user)
        messages.success(request, f"{demande.demandeur} est maintenant administrateur.")
    elif action == 'refuser':
        demande.statut = 'refusee'
        email_promotion_admin_refusee(demande.demandeur.user)
        messages.info(request, f"Demande de {demande.demandeur} refusée.")

    demande.traitee_par = admin
    demande.save()
    return redirect('liste_demandes_promotion')