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
  
  
  
  
