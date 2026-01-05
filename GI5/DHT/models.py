from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Dht11(models.Model):
    temp = models.FloatField(null=True)
    hum = models.FloatField(null=True)
    dt = models.DateTimeField(auto_now_add=True, null=True)

class Operateur(models.Model):
    """Modèle pour les opérateurs qui gèrent les incidents"""
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    ordre_escalade = models.IntegerField(help_text="Ordre d'escalade (1, 2 ou 3)")
    actif = models.BooleanField(default=True)
    # Lien avec un utilisateur Django pour l'authentification
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='operateur_profile',
        help_text="Utilisateur Django associé pour l'authentification"
    )
    
    class Meta:
        ordering = ['ordre_escalade']
        verbose_name = "Opérateur"
        verbose_name_plural = "Opérateurs"
    
    def __str__(self):
        return f"{self.nom} (Opérateur {self.ordre_escalade})"
    
    def peut_modifier_incident(self, incident):
        """Vérifie si cet opérateur peut modifier l'incident"""
        return incident.operateur_actuel == self

class Incident(models.Model):
    """Modèle pour les incidents de température"""
    
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('ferme', 'Fermé'),
    ]
    
    TYPE_INCIDENT_CHOICES = [
        ('trop_bas', 'Température trop basse (< 2°C)'),
        ('trop_haut', 'Température trop haute (> 8°C)'),
    ]
    
    # Informations sur l'incident
    dht11 = models.ForeignKey(Dht11, on_delete=models.CASCADE, related_name='incidents')
    temperature = models.FloatField(help_text="Température qui a déclenché l'incident")
    type_incident = models.CharField(max_length=20, choices=TYPE_INCIDENT_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert')
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    
    # Gestion des opérateurs et escalade
    operateur_actuel = models.ForeignKey(
        Operateur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='incidents_actuels'
    )
    operateur_initial = models.ForeignKey(
        Operateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents_initiaux'
    )
    tentatives_operateur1 = models.IntegerField(default=0)
    tentatives_operateur2 = models.IntegerField(default=0)
    tentatives_operateur3 = models.IntegerField(default=0)
    
    # Commentaires et accusé de réception
    commentaires = models.TextField(blank=True)
    accuse_reception = models.BooleanField(default=False)
    date_accuse_reception = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"
    
    def __str__(self):
        return f"Incident #{self.id} - {self.get_type_incident_display()} - {self.temperature}°C"
    
    def get_tentatives_total(self):
        """Retourne le nombre total de tentatives"""
        return self.tentatives_operateur1 + self.tentatives_operateur2 + self.tentatives_operateur3
    
    def peut_escalader(self):
        """Vérifie si l'incident peut être escaladé"""
        if self.operateur_actuel is None:
            return True
        
        ordre = self.operateur_actuel.ordre_escalade
        if ordre == 1:
            return self.tentatives_operateur1 >= 3
        elif ordre == 2:
            return self.tentatives_operateur2 >= 3
        elif ordre == 3:
            return self.tentatives_operateur3 >= 3
        return False
    
    def incrementer_tentative(self):
        """Incrémente le compteur de tentatives de l'opérateur actuel"""
        if self.operateur_actuel is None:
            return
        
        ordre = self.operateur_actuel.ordre_escalade
        if ordre == 1:
            self.tentatives_operateur1 += 1
        elif ordre == 2:
            self.tentatives_operateur2 += 1
        elif ordre == 3:
            self.tentatives_operateur3 += 1
        self.save()