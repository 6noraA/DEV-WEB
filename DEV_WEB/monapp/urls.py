from django.urls import path
from . import views

urlpatterns = [
    # Accueil
    path('', views.accueil, name='home'),
    path('accueil/', views.accueil, name='accueil'),

    # Produits
    path('creer/', views.creer_produit, name='creer_produit'),
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produit/<str:id>/', views.detail_produit, name='detail_produit'),
    path('produit/<str:id>/modifier/', views.modifier_produit, name='modifier_produit'),

    # Inscription / Connexion
    path('inscription/', views.inscription, name='inscription'),
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

    # Administration (niveau expert uniquement)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/bannir/<int:user_id>/', views.bannir_utilisateur, name='bannir_utilisateur'),
    path('admin-dashboard/reactiver/<int:user_id>/', views.reactiver_utilisateur, name='reactiver_utilisateur'),
    path('admin-dashboard/supprimer/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
]