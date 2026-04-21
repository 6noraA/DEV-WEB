
from django.urls import path
from . import views

urlpatterns = [
    path('creer/', creer_produit, name='creer_produit'),
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produit/<str:id>/', views.detail_produit, name='detail_produit'),
    path('inscrpition/', views.inscription, name='register'),
    path('connexion/', views.connexion, name='login'),
    path('deconnexion/', views.deconnexion, name='logout'),
]
