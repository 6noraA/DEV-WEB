from django.db import models
from django.contrib.auth.models import User


class Personne(models.Model):
    GENRE_CHOIX = [('H', 'Homme'), ('F', 'Femme')]

    TYPE_MEMBRE = [
        ('visiteur', 'Visiteur'),
        ('simple', 'Simple'),
        ('complexe', 'Complexe'),
        ('administrateur', 'Administrateur'),
    ]

    user           = models.OneToOneField(User, on_delete=models.CASCADE)
    age            = models.IntegerField(default=0)
    sexe           = models.CharField(max_length=10, choices=GENRE_CHOIX, default='H')
    type_membre    = models.CharField(max_length=30, choices=TYPE_MEMBRE, default='visiteur')
    photo          = models.ImageField(upload_to='photo/personne/', null=True, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    points         = models.FloatField(default=0)
    nb_connexions  = models.IntegerField(default=0)
    nb_actions     = models.IntegerField(default=0)
    niveau             = models.CharField(max_length=20, default='debutant')
    email_confirme     = models.BooleanField(default=False)
    token_confirmation = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.user.username


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profil(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            Personne.objects.create(
                user=instance,
                niveau='expert',
                points=7,
                type_membre='administrateur',
            )
        else:
            Personne.objects.create(user=instance)

@receiver(post_save, sender=User)
def upgrade_superuser_profil(sender, instance, created, **kwargs):
    if not created:
        try:
            personne = instance.personne
            if instance.is_superuser and personne.niveau != 'expert':
                personne.niveau = 'expert'
                personne.points = 7
                personne.type_membre = 'administrateur'
                personne.save()
        except Personne.DoesNotExist:
            pass


class EtatObjet(models.TextChoices):
    ACTIF       = 'ACTIF',       'Actif'
    INACTIF     = 'INACTIF',     'Inactif'
    PANNE       = 'PANNE',       'Panne'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'
    DECONNECTE  = 'DECONNECTE',  'Déconnecté'


class MODE(models.TextChoices):
    AUTOMATIQUE = 'AUTO',   'Automatique'
    MANUEL      = 'MANUEL', 'Manuel'


class Produit(models.Model):
    ID                       = models.CharField(max_length=100, primary_key=True)
    Nom                      = models.CharField(max_length=100)
    Connectiviter_type       = models.CharField(max_length=100)
    etat                     = models.CharField(max_length=20, choices=EtatObjet.choices, default=EtatObjet.INACTIF)
    marque                   = models.CharField(max_length=100)
    mode                     = models.CharField(max_length=20, choices=MODE.choices, default=MODE.AUTOMATIQUE)
    Bactterie                = models.IntegerField()
    Adresse_IP               = models.GenericIPAddressField()
    Temp_restante            = models.DateField()
    Date_dernier_maintenance = models.DateField()
    Date_dernier_utilisation = models.DateField()
    Description              = models.TextField()
    photo                    = models.ImageField(upload_to='photos/outils/', null=True, blank=True)

    def __str__(self):
        return self.Nom


class Lieu(models.Model):
    Nom            = models.CharField(max_length=100)
    Adresse        = models.CharField(max_length=200, unique=True)
    Description    = models.TextField()
    latitude       = models.FloatField()
    longitude      = models.FloatField()
    photo          = models.ImageField(upload_to='photos/lieux/', null=True, blank=True)
    liste_produits = models.ManyToManyField('Produit', related_name='lieux')

    def __str__(self):
        return self.Nom


class Information(models.Model):
    nom         = models.CharField(max_length=100)
    description = models.TextField()
    photo       = models.ImageField(upload_to='photos/information/', null=True, blank=True)
    date        = models.DateField(auto_now_add=True)
    auteur      = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Information_locale(Information):
    pass


class Signalement(Information):
    TYPE_CHOICES = [
        ('accident', 'Accident'),
        ('danger',   'Danger'),
        ('autre',    'Autre'),
    ]
    type_signalement = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='autre',
    )
    lieu    = models.ForeignKey(
        'Lieu',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='signalements',
    )
    produit = models.ForeignKey(
        'Produit',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='signalements',
    )


class DemandePromotion(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee',   'Acceptée'),
        ('refusee',    'Refusée'),
    ]
    demandeur   = models.ForeignKey(
        Personne,
        on_delete=models.CASCADE,
        related_name='demandes_promotion',
    )
    message     = models.TextField(blank=True, help_text="Motif de la demande")
    statut      = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date        = models.DateTimeField(auto_now_add=True)
    traitee_par = models.ForeignKey(
        Personne,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='demandes_traitees',
    )

    def __str__(self):
        return f"Demande de {self.demandeur} — {self.statut}"