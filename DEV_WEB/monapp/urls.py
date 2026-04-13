
from django.urls import path
from . import views

urlpatterns = [
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produit/<str:id>/', views.detail_produit, name='detail_produit'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
