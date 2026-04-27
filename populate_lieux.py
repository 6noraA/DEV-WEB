"""
Script de peuplement — 10 lieux fictifs pour MaVille
Coordonnées adaptées à la carte custom (bounds [[-100,-100],[100,100]])
Exécuter avec : python manage.py shell < populate_lieux.py
"""

from monapp.models import Lieu, Produit

# La carte image couvre [-100, -100] → [100, 100]
# Zone urbaine centrale visible sur la carte image

lieux_data = [
    {
        "Nom": "Mairie Centrale",
        "Adresse": "1 Place de la République",
        "Description": "Bâtiment administratif principal de la ville. Accueil des citoyens du lundi au vendredi.",
        "latitude": 25.0,
        "longitude": 10.0,
    },
    {
        "Nom": "Bibliothèque Municipale",
        "Adresse": "12 Rue des Livres",
        "Description": "Espace culturel proposant plus de 50 000 ouvrages, espaces de travail et ateliers numériques.",
        "latitude": 30.0,
        "longitude": 5.0,
    },
    {
        "Nom": "Parc des Lumières",
        "Adresse": "45 Avenue du Parc",
        "Description": "Grand parc municipal équipé de capteurs environnementaux et d'éclairage intelligent.",
        "latitude": 35.0,
        "longitude": 20.0,
    },
    {
        "Nom": "Centre Sportif Jean Moulin",
        "Adresse": "8 Rue du Stade",
        "Description": "Complexe sportif avec piscine, gymnase et terrains de plein air connectés.",
        "latitude": 20.0,
        "longitude": 30.0,
    },
    {
        "Nom": "École Primaire Victor Hugo",
        "Adresse": "23 Rue de l'École",
        "Description": "Établissement scolaire équipé de tableaux interactifs et capteurs de qualité d'air.",
        "latitude": 15.0,
        "longitude": -5.0,
    },
    {
        "Nom": "Port Commercial",
        "Adresse": "56 Quai des Dockers",
        "Description": "Zone portuaire avec système de gestion des flux maritimes et conteneurs connectés.",
        "latitude": -5.0,
        "longitude": -15.0,
    },
    {
        "Nom": "Station de Bus Centrale",
        "Adresse": "2 Boulevard des Transports",
        "Description": "Hub de transport connecté avec écrans d'information en temps réel et bornes de recharge.",
        "latitude": 10.0,
        "longitude": 0.0,
    },
    {
        "Nom": "Centre Médical de Proximité",
        "Adresse": "34 Rue de la Santé",
        "Description": "Structure de santé de quartier équipée de dispositifs médicaux connectés.",
        "latitude": 40.0,
        "longitude": -10.0,
    },
    {
        "Nom": "Parking Intelligent Nord",
        "Adresse": "78 Rue du Commerce",
        "Description": "Parking municipal à 4 niveaux avec capteurs de détection de places et paiement connecté.",
        "latitude": 50.0,
        "longitude": 15.0,
    },
    {
        "Nom": "Place des Fontaines",
        "Adresse": "3 Place des Fontaines",
        "Description": "Espace public piétonnier avec fontaines connectées, wifi public et bornes d'information touristique.",
        "latitude": 5.0,
        "longitude": 15.0,
    },
]

print("🏙️  Création des lieux...")
created, skipped = 0, 0

for data in lieux_data:
    lieu, was_created = Lieu.objects.get_or_create(
        Adresse=data["Adresse"],
        defaults={
            "Nom":         data["Nom"],
            "Description": data["Description"],
            "latitude":    data["latitude"],
            "longitude":   data["longitude"],
        }
    )

    if was_created:
        produits = Produit.objects.all()[:2]
        if produits:
            lieu.liste_produits.set(produits)
        created += 1
        print(f"  ✅ Créé  : {lieu.Nom} ({data['latitude']}, {data['longitude']})")
    else:
        skipped += 1
        print(f"  ⏭️  Existe : {lieu.Nom}")

print(f"\n✔️  Terminé — {created} créés, {skipped} ignorés.")