import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from twilio.rest import Client
from .models import Incident, Operateur, Dht11
def send_telegram(text: str) -> bool:
    """Envoie un message Telegram via l'API officielle. Retourne True si OK."""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": chat_id, "text": text})
        return r.ok
    except Exception:
        return False


def send_call_alert(temp):
    # Si les identifiants ne sont pas configurés, on sort pour éviter un crash.
    account_sid = ''
    auth_token = ''
    to_number = ''
    from_number = ''
    if not account_sid or not auth_token or not to_number or not from_number:
        print("Twilio non configuré: appel ignoré.")
        return False

    try:
        client = Client(account_sid, auth_token)
        call = client.calls.create(
            twiml=f'<Response><Say>Attention, la température est de {temp} degrés, seuil dépassé !</Say></Response>',
            to=to_number,
            from_=from_number
        )
        print(call.sid)
        return True
    except Exception as exc:
        print(f"Erreur Twilio: {exc}")
        return False


# ============================================================
# =============  GESTION DES INCIDENTS ET ESCALADE  ==========
# ============================================================

def detecter_incident(dht11_instance):
    """
    Détecte si une température est hors plage (2-8°C) et crée un incident si nécessaire.
    Retourne l'incident créé ou None.
    """
    if dht11_instance.temp is None:
        return None
    
    temp = dht11_instance.temp
    type_incident = None
    
    # Détection de l'incident (hors plage 2-8°C)
    if temp < 2:
        type_incident = 'trop_bas'
    elif temp > 8:
        type_incident = 'trop_haut'
    else:
        # Température normale, pas d'incident
        return None
    
    # Vérifier s'il existe déjà un incident ouvert pour cette mesure
    # On vérifie les incidents récents (dernières 2 heures) avec le même type d'incident
    deux_heures = timezone.now() - timedelta(hours=2)
    incidents_recents = Incident.objects.filter(
        statut__in=['ouvert', 'en_cours'],
        date_creation__gte=deux_heures,
        type_incident=type_incident
    ).order_by('-date_creation')
    
    incident_existant = incidents_recents.first()
    
    if incident_existant:
        # Compter le nombre d'incidents créés en continu (dans les 10 dernières minutes)
        dix_minutes = timezone.now() - timedelta(minutes=10)
        incidents_continus = Incident.objects.filter(
            statut__in=['ouvert', 'en_cours'],
            date_creation__gte=dix_minutes,
            type_incident=type_incident
        ).count()
        
        # Si 3 incidents ou plus créés en continu, incrémenter les tentatives et escalader
        if incidents_continus >= 3:
            # Incrémenter les tentatives de l'opérateur actuel
            if incident_existant.operateur_actuel:
                ordre = incident_existant.operateur_actuel.ordre_escalade
                if ordre == 1:
                    incident_existant.tentatives_operateur1 = min(incident_existant.tentatives_operateur1 + 1, 3)
                elif ordre == 2:
                    incident_existant.tentatives_operateur2 = min(incident_existant.tentatives_operateur2 + 1, 3)
                elif ordre == 3:
                    incident_existant.tentatives_operateur3 = min(incident_existant.tentatives_operateur3 + 1, 3)
                
                commentaire = f"[Escalade automatique] {incidents_continus} incident(s) cree(s) en continu. Tentative automatique ajoutee."
                if incident_existant.commentaires:
                    incident_existant.commentaires += f"\n\n[{timezone.now().strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
                else:
                    incident_existant.commentaires = f"[{timezone.now().strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
                
                incident_existant.save()
                
                # Vérifier si on peut escalader
                incident_existant.refresh_from_db()
                if incident_existant.peut_escalader():
                    escalader_incident(incident_existant)
        
        # Vérifier aussi l'escalade automatique basée sur le temps
        verifier_escalade_automatique(incident_existant)
        return incident_existant
    
    # Créer un nouvel incident
    operateur1 = Operateur.objects.filter(ordre_escalade=1, actif=True).first()
    
    incident = Incident.objects.create(
        dht11=dht11_instance,
        temperature=temp,
        type_incident=type_incident,
        operateur_actuel=operateur1,
        operateur_initial=operateur1,
        statut='ouvert'
    )
    
    # Compter les incidents créés en continu (dans les 10 dernières minutes)
    dix_minutes = timezone.now() - timedelta(minutes=10)
    incidents_continus = Incident.objects.filter(
        statut__in=['ouvert', 'en_cours'],
        date_creation__gte=dix_minutes,
        type_incident=type_incident
    ).count()
    
    # Si 3 incidents ou plus créés en continu, incrémenter les tentatives et escalader
    if incidents_continus >= 3:
        # Incrémenter les tentatives de l'opérateur actuel
        if incident.operateur_actuel:
            ordre = incident.operateur_actuel.ordre_escalade
            if ordre == 1:
                incident.tentatives_operateur1 = min(incident.tentatives_operateur1 + 1, 3)
            elif ordre == 2:
                incident.tentatives_operateur2 = min(incident.tentatives_operateur2 + 1, 3)
            elif ordre == 3:
                incident.tentatives_operateur3 = min(incident.tentatives_operateur3 + 1, 3)
            
            commentaire = f"[Escalade automatique] {incidents_continus} incident(s) cree(s) en continu. Tentative automatique ajoutee."
            if incident.commentaires:
                incident.commentaires += f"\n\n[{timezone.now().strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
            else:
                incident.commentaires = f"[{timezone.now().strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
            
            incident.save()
            
            # Vérifier si on peut escalader
            incident.refresh_from_db()
            if incident.peut_escalader():
                escalader_incident(incident)
    
    # Envoyer notification à TOUS les opérateurs actifs
    envoyer_notification_tous_operateurs(incident)
    
    return incident


def envoyer_notification_operateur(incident, operateur):
    """
    Envoie une notification email à l'opérateur concerné.
    """
    try:
        type_msg = "trop basse" if incident.type_incident == 'trop_bas' else "trop haute"
        seuil = "2°C" if incident.type_incident == 'trop_bas' else "8°C"
        
        # Vérifier si l'opérateur est assigné à cet incident
        est_assigné = incident.operateur_actuel == operateur
        assignation_msg = "Vous êtes assigné à cet incident." if est_assigné else "Cet incident est assigné à un autre opérateur pour le moment."
        
        subject = f"⚠️ Incident #{incident.id} - Température {type_msg}"
        message = f"""
Bonjour {operateur.nom},

Un incident a été détecté concernant la température du capteur DHT11.

Détails de l'incident:
- ID Incident: #{incident.id}
- Température mesurée: {incident.temperature:.1f}°C
- Type: Température {type_msg} (seuil: {seuil})
- Date de détection: {incident.date_creation.strftime('%d/%m/%Y %H:%M:%S')}
- Statut: {incident.get_statut_display()}
- Opérateur assigné: {incident.operateur_actuel.nom if incident.operateur_actuel else 'Non assigné'}
- {assignation_msg}

Veuillez vous connecter au système pour consulter cet incident.
URL: http://127.0.0.1:8000/gestion-incidents/{incident.id}/

Cordialement,
Système de monitoring DHT11
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[operateur.email],
            fail_silently=True,
        )
        print(f"Notification envoyée à {operateur.email} pour l'incident #{incident.id}")
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de notification à {operateur.email}: {e}")
        return False


def envoyer_notification_tous_operateurs(incident):
    """
    Envoie une notification email à TOUS les opérateurs actifs lors de la création d'un incident.
    """
    operateurs = Operateur.objects.filter(actif=True)
    for operateur in operateurs:
        envoyer_notification_operateur(incident, operateur)
    print(f"Notifications envoyées à {operateurs.count()} opérateur(s) pour l'incident #{incident.id}")


def escalader_incident(incident):
    """
    Escalade un incident vers l'opérateur suivant si les 3 tentatives sont atteintes.
    Envoie une notification à tous les opérateurs lors de l'escalade.
    Retourne True si l'escalade a été effectuée, False sinon.
    """
    if not incident.peut_escalader():
        return False
    
    if incident.operateur_actuel is None:
        # Assigner au premier opérateur
        operateur1 = Operateur.objects.filter(ordre_escalade=1, actif=True).first()
        if operateur1:
            incident.operateur_actuel = operateur1
            incident.save()
            envoyer_notification_tous_operateurs(incident)
            return True
        return False
    
    ordre_actuel = incident.operateur_actuel.ordre_escalade
    
    if ordre_actuel == 1:
        # Escalade vers opérateur 2
        operateur2 = Operateur.objects.filter(ordre_escalade=2, actif=True).first()
        if operateur2:
            incident.operateur_actuel = operateur2
            incident.statut = 'en_cours'
            incident.save()
            # Notifier tous les opérateurs de l'escalade
            envoyer_notification_tous_operateurs(incident)
            print(f"Incident #{incident.id} escaladé vers {operateur2.nom}")
            return True
    
    elif ordre_actuel == 2:
        # Escalade vers opérateur 3
        operateur3 = Operateur.objects.filter(ordre_escalade=3, actif=True).first()
        if operateur3:
            incident.operateur_actuel = operateur3
            incident.statut = 'en_cours'
            incident.save()
            # Notifier tous les opérateurs de l'escalade
            envoyer_notification_tous_operateurs(incident)
            print(f"Incident #{incident.id} escaladé vers {operateur3.nom}")
            return True
    
    # Aucun opérateur suivant disponible
    print(f"Impossible d'escalader l'incident #{incident.id}: aucun opérateur suivant disponible")
    return False


def traiter_incident(incident, commentaire="", resoudre=False):
    """
    Traite un incident en incrémentant les tentatives et gérant l'escalade si nécessaire.
    """
    if incident.operateur_actuel:
        incident.incrementer_tentative()
        
        if commentaire:
            if incident.commentaires:
                incident.commentaires += f"\n\n[{timezone.now().strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
            else:
                incident.commentaires = f"[{timezone.now().strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
        
        if resoudre:
            incident.statut = 'resolu'
            incident.date_resolution = timezone.now()
            incident.save()
            return True
        elif incident.peut_escalader():
            # Escalader vers l'opérateur suivant
            escalader_incident(incident)
        
        incident.save()
        return True
    
    return False


def accuser_reception(incident):
    """
    Marque un incident comme accusé de réception par l'opérateur.
    """
    incident.accuse_reception = True
    incident.date_accuse_reception = timezone.now()
    incident.statut = 'en_cours'
    incident.save()
    return True


def verifier_escalade_automatique(incident, delai_minutes=30):
    """
    Vérifie si un incident doit être escaladé automatiquement basé sur le temps.
    Si l'incident n'a pas été traité depuis X minutes, incrémente automatiquement les tentatives.
    """
    maintenant = timezone.now()
    derniere_action = incident.date_modification or incident.date_creation
    temps_ecoule = maintenant - derniere_action
    delai = timedelta(minutes=delai_minutes)
    
    # Si l'incident n'a pas été traité depuis le délai
    if temps_ecoule >= delai:
        # Calculer combien de tentatives automatiques ajouter
        # (1 tentative toutes les X minutes)
        tentatives_auto = int(temps_ecoule.total_seconds() / (delai_minutes * 60))
        
        if incident.operateur_actuel:
            ordre = incident.operateur_actuel.ordre_escalade
            
            # Ajouter les tentatives automatiques (max 3 par opérateur)
            if ordre == 1:
                tentatives_a_ajouter = min(tentatives_auto, 3 - incident.tentatives_operateur1)
                if tentatives_a_ajouter > 0:
                    incident.tentatives_operateur1 = min(incident.tentatives_operateur1 + tentatives_a_ajouter, 3)
                    commentaire = f"[Escalade automatique] Aucune action depuis {int(temps_ecoule.total_seconds() / 60)} minutes. {tentatives_a_ajouter} tentative(s) automatique(s) ajoutée(s)."
                    if incident.commentaires:
                        incident.commentaires += f"\n\n[{maintenant.strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
                    else:
                        incident.commentaires = f"[{maintenant.strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
                    incident.save()
            
            elif ordre == 2:
                tentatives_a_ajouter = min(tentatives_auto, 3 - incident.tentatives_operateur2)
                if tentatives_a_ajouter > 0:
                    incident.tentatives_operateur2 = min(incident.tentatives_operateur2 + tentatives_a_ajouter, 3)
                    commentaire = f"[Escalade automatique] Aucune action depuis {int(temps_ecoule.total_seconds() / 60)} minutes. {tentatives_a_ajouter} tentative(s) automatique(s) ajoutée(s)."
                    if incident.commentaires:
                        incident.commentaires += f"\n\n[{maintenant.strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
                    else:
                        incident.commentaires = f"[{maintenant.strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
                    incident.save()
            
            elif ordre == 3:
                tentatives_a_ajouter = min(tentatives_auto, 3 - incident.tentatives_operateur3)
                if tentatives_a_ajouter > 0:
                    incident.tentatives_operateur3 = min(incident.tentatives_operateur3 + tentatives_a_ajouter, 3)
                    commentaire = f"[Escalade automatique] Aucune action depuis {int(temps_ecoule.total_seconds() / 60)} minutes. {tentatives_a_ajouter} tentative(s) automatique(s) ajoutée(s)."
                    if incident.commentaires:
                        incident.commentaires += f"\n\n[{maintenant.strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
                    else:
                        incident.commentaires = f"[{maintenant.strftime('%d/%m/%Y %H:%M:%S')}] {commentaire}"
                    incident.save()
        
        # Vérifier si on peut escalader après l'ajout des tentatives
        incident.refresh_from_db()
        if incident.peut_escalader():
            escalader_incident(incident)
            return True
    
    return False