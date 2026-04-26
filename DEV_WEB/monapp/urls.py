from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil à la racine du site
    path('', views.accueil, name='home'),

    # Produits
    path('creer/', creer_produit, name='creer_produit'),
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produit/<str:id>/', views.detail_produit, name='detail_produit'),

    # Inscription
    path('inscription/', views.inscription, name='inscription'),
    path('register/', views.inscription, name='register'),

    # Connexion / déconnexion
    path('connexion/', views.connexion, name='connexion'),
    path('login/', views.connexion, name='login'),
    path('deconnexion/', views.deconnexion, name='logout'),

    # Pages principales
    path('accueil/', views.accueil, name='accueil'),
    path('transport/', views.transport, name='transport'),
    path('incident/', views.incident, name='incident'),
    path('services-public/', views.services_public, name='services-public'),
    path('info-locale/', views.info_locale, name='info-locale'),

     # Profil utilisateur
    path('profil/', views.profil, name='profil'),
    path('reservation/', views.reservation, name='reservation'),
    path('vie-citoyenne/', views.vie_citoyenne, name='vie-citoyenne'),
]