from django.db import models

# Create your models here.
GENRE_CHOIX = (('H', _('Homme')),
               ('F', _('Femme')))

TYPE_MEMBRE = (('citoyen', _('Citoyen')),
               ('etudiant', _('Etudiant')),
               ('technicien', _('Technicien')),
               ('administrateur', _('administrateur')))

class Personne(models.Model) :
  personne_login = models.charField(max_length=40,primary_keys=True)
  personne_age = models.IntegerField()
  personne_genre = models.CharField(_('genre'),max_length=1, choices=GENRE_CHOIX)
  personne_type = models.CharField(_('type'),max_length=20, choices = TYPE_MEMBRE)
  personne_photo = models.ImageField(upload_to='photo/personne/',null True,blank=True)
  personne_dateNaissance = models.DateField()
  personne_nom = models.charField(max_length=40)
  personne_prenom = models.charField(max_length=40)
  personne_mdp =
  
                        
  
  
  
  
