from django.db import models

# Create your models here.
GENRE_CHOIX = [('H','Homme'),
               ('F', 'Femme')]

TYPE_MEMBRE = [('citoyen','Citoyen'),
               ('etudiant', 'Etudiant'),
               ('technicien','Technicien'),
               ('administrateur','administrateur')]

class Personne(models.Model) :
  personne_login = models.charField(max_length=40,primary_keys=True,unique=True)
  personne_age = models.IntegerField()
  personne_genre = models.CharField(max_length=20, choices=GENRE_CHOIX)
  personne_type = models.CharField(max_length=1, choices=TYPE_MEMBRE)
  personne_photo = models.ImageField(upload_to='photo/personne/',null=True,blank=True)
  personne_dateNaissance = models.DateField()

  #Partie privée
  personne_nom = models.CharField(max_length=40)
  personne_prenom = models.charField(max_length=40)
  personne_mdp = models.CharField(max_length=40)

  
  def set_password(self, raw_password):
        """Hash le mot de passe avant de le sauvegarder"""
        self.personne_mdp = make_password(raw_password)

  def __str__(self):
        return self.personne_login




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
  
  
  
  
