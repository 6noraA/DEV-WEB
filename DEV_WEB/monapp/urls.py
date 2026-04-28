from django.urls import path
from . import views

urlpatterns = [
    # Accueil
    path('', views.accueil, name='home'),
    path('accueil/', views.accueil, name='accueil'),

    # Produits
    path('creer/', views.creer_produit, name='creer_produit'),
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produits/statistiques/', views.statistiques, name='statistiques'),
    path('api/produits/live/', views.api_produits_live, name='api_produits_live'),
    path('produit/<str:id>/', views.detail_produit, name='detail_produit'),
    path('produit/<str:id>/modifier/', views.modifier_produit, name='modifier_produit'),

    # Inscription / Connexion
    path('inscription/', views.inscription, name='inscription'),
    path('confirmer-email/<str:token>/', views.confirmer_email, name='confirmer_email'),
    path('register/', views.inscription, name='register'),
    path('connexion/', views.connexion, name='connexion'),
    path('login/', views.connexion, name='login'),
    path('deconnexion/', views.deconnexion, name='logout'),

    # Pages principales
    path('transport/', views.transport, name='transport'),
    path('incident/', views.incident, name='incident'),
    path('services-public/', views.services_public, name='services-public'),
    path('info-locale/', views.info_locale, name='info-locale'),
    path('reservation/', views.reservation, name='reservation'),
    path('vie-citoyenne/', views.vie_citoyenne, name='vie-citoyenne'),

    # Profil
    path('profil/', views.profil, name='profil'),
    path('profil/modifier/', views.edit_profil, name='edit_profil'),
    path('profil/niveau/', views.changer_niveau, name='changer_niveau'),
    path('profil/<int:user_id>/', views.voir_profil, name='voir_profil'),

    # Administration
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/bannir/<int:user_id>/', views.bannir_utilisateur, name='bannir_utilisateur'),
    path('admin-dashboard/reactiver/<int:user_id>/', views.reactiver_utilisateur, name='reactiver_utilisateur'),
    path('admin-dashboard/supprimer/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),

    # Lieux
    path('lieux/', views.liste_lieux, name='liste_lieux'),
    path('lieux/creer/', views.creer_lieu, name='creer_lieu'),
    path('lieux/carte/', views.carte_lieux, name='carte_lieux'),
    path('lieux/<int:lieu_id>/', views.detail_lieu, name='detail_lieu'),
    path('lieux/<int:lieu_id>/ajouter/<str:produit_id>/', views.ajouter_produit_lieu, name='ajouter_produit_lieu'),
    path('lieux/<int:lieu_id>/retirer/<str:produit_id>/', views.retirer_produit_lieu, name='retirer_produit_lieu'),

    # Signalements
    path('signalements/', views.liste_signalements, name='liste_signalements'),
    path('liste_signalements/', views.liste_signalements),
    path('signalements/creer/', views.creer_signalement, name='creer_signalement'),
    path('creer_signalement/', views.creer_signalement),
    path('signalements/<int:signalement_id>/', views.detail_signalement, name='detail_signalement'),
    path('signalements/<int:signalement_id>/modifier/', views.modifier_signalement, name='modifier_signalement'),

    # Demandes de promotion
    path('promotion/demander/', views.demander_promotion, name='demander_promotion'),
    path('promotion/demandes/', views.liste_demandes_promotion, name='liste_demandes_promotion'),
    path('promotion/demandes/<int:demande_id>/<str:action>/', views.traiter_demande_promotion, name='traiter_demande_promotion'),

    # Informations locales
    path('informations-locales/', views.liste_informations_locales, name='liste_informations_locales'),
    path('liste_informations_locales/', views.liste_informations_locales),
    path('informations-locales/creer/', views.creer_information_locale, name='creer_information_locale'),
    path('creer_information_locale/', views.creer_information_locale),
    path('informations-locales/<int:information_locale_id>/', views.detail_information_locale, name='detail_information_locale'),
]