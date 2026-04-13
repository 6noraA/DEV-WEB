from django.shortcuts import render
from .form import ProduitForm
from .models import Produit

def creer_produit(request):
    if request.method == 'POST' :
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    elif request.method == 'GET':
        form = ProduitForm()

    return render(request, 'produits/creer_produit.html', {'form': form})
# Create your views here.


