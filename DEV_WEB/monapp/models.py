from django.db import models
from django.contrib.auth.models import User

class Personne(models.Model):
    GENRE_CHOIX = [('H', 'Homme'),
                   ('F', 'Femme')]

    TYPE_MEMBRE = [('visiteur', 'visiteur'),
                   ('simple', 'simple'),
                   ('complexe', 'complexe'),
                   ('administrateur', 'administrateur')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    age = models.IntegerField(default=0)                          # CORRIGÉ : default=0
    sexe = models.CharField(max_length=10, choices=GENRE_CHOIX, default='H')  # CORRIGÉ : default='H'
    type_membre = models.CharField(max_length=30, choices=TYPE_MEMBRE, default='visiteur')  # CORRIGÉ : default='visiteur'
    photo = models.ImageField(upload_to='photo/personne/', null=True, blank=True)
    date_naissance = models.DateField(null=True, blank=True)      # CORRIGÉ : null=True pour éviter l'erreur
    points = models.FloatField(default=0)
    nb_connexions = models.IntegerField(default=0)
    nb_actions = models.IntegerField(default=0)
    niveau = models.CharField(max_length=20, default='debutant')

    def __str__(self):
        return self.user.username


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profil(sender, instance, created, **kwargs):
    if created:
        Personne.objects.create(user=instance)


class EtatObjet(models.TextChoices):
    ACTIF = 'ACTIF', 'Actif'
    INACTIF = 'INACTIF', 'Inactif'
    PANNE = 'PANNE', 'Panne'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'
    DECONNECTE = 'DECONNECTE', 'Déconnecté'


class MODE(models.TextChoices):
    AUTOMATIQUE = 'AUTO', 'Automatique'
    MANUEL = 'MANUEL', 'Manuel'


class Produit(models.Model):
    ID = models.CharField(max_length=100, primary_key=True)
    Nom = models.CharField(max_length=100)
    Connectiviter_type = models.CharField(max_length=100)
    etat = models.CharField(max_length=20, choices=EtatObjet.choices, default=EtatObjet.INACTIF)
    marque = models.CharField(max_length=100)
    mode = models.CharField(max_length=20, choices=MODE.choices, default=MODE.AUTOMATIQUE)
    Bactterie = models.IntegerField()
    Adresse_IP = models.GenericIPAddressField()
    Temp_restante = models.DateField()
    Date_dernier_maintenance = models.DateField()
    Date_dernier_utilisation = models.DateField()
    Description = models.TextField()
    photo = models.ImageField(upload_to='photos/outils/', null=True, blank=True)

    def __str__(self):
        return self.Nom
