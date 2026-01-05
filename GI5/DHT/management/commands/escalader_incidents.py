"""
Commande de management pour escalader automatiquement les incidents non traités.

Usage:
    python manage.py escalader_incidents

Cette commande :
- Vérifie les incidents ouverts/en cours
- Si un incident n'a pas été traité depuis X minutes, incrémente automatiquement les tentatives
- Escalade vers l'opérateur suivant si 3 tentatives sont atteintes
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from DHT.models import Incident
from DHT.utils import escalader_incident, traiter_incident

class Command(BaseCommand):
    help = 'Escalade automatique des incidents non traités'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delai-minutes',
            type=int,
            default=30,
            help='Délai en minutes avant d\'incrémenter automatiquement une tentative (défaut: 30)',
        )

    def handle(self, *args, **options):
        delai_minutes = options['delai_minutes']
        maintenant = timezone.now()
        delai = timedelta(minutes=delai_minutes)
        
        # Récupérer les incidents ouverts ou en cours
        incidents = Incident.objects.filter(
            statut__in=['ouvert', 'en_cours']
        )
        
        self.stdout.write(f"Vérification de {incidents.count()} incident(s)...")
        
        incidents_escalades = 0
        tentatives_ajoutees = 0
        
        for incident in incidents:
            # Calculer le temps écoulé depuis la dernière modification
            derniere_action = incident.date_modification or incident.date_creation
            temps_ecoule = maintenant - derniere_action
            
            # Si l'incident n'a pas été traité depuis le délai, incrémenter une tentative
            if temps_ecoule >= delai:
                # Vérifier si on peut déjà escalader
                if incident.peut_escalader():
                    # Escalader vers l'opérateur suivant
                    if escalader_incident(incident):
                        incidents_escalades += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'[OK] Incident #{incident.id} escalade vers {incident.operateur_actuel.nom if incident.operateur_actuel else "N/A"}'
                            )
                        )
                else:
                    # Incrementer une tentative automatique
                    commentaire_auto = f"[Escalade automatique] Aucune action depuis {int(temps_ecoule.total_seconds() / 60)} minutes. Tentative automatique ajoutee."
                    traiter_incident(incident, commentaire=commentaire_auto)
                    tentatives_ajoutees += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'[!] Incident #{incident.id} : Tentative automatique ajoutee (Operateur {incident.operateur_actuel.ordre_escalade if incident.operateur_actuel else "N/A"})'
                        )
                    )
                    
                    # Vérifier à nouveau si on peut escalader après l'incrémentation
                    incident.refresh_from_db()
                    if incident.peut_escalader():
                        if escalader_incident(incident):
                            incidents_escalades += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'[OK] Incident #{incident.id} escalade vers {incident.operateur_actuel.nom if incident.operateur_actuel else "N/A"}'
                                )
                            )
        
        self.stdout.write(self.style.SUCCESS(
            f'\nRésumé: {tentatives_ajoutees} tentative(s) ajoutée(s), {incidents_escalades} incident(s) escaladé(s)'
        ))

