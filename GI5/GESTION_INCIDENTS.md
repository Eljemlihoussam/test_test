# 🚨 Système de Gestion des Incidents DHT11

## Vue d'ensemble

Le système de gestion des incidents détecte automatiquement les températures hors plage (2-8°C) et gère l'escalade entre 3 opérateurs avec un système de tentatives.

## Fonctionnalités

### 1. Détection automatique
- **Température < 2°C** → Incident "Température trop basse"
- **Température > 8°C** → Incident "Température trop haute"
- Détection automatique lors de l'ajout de données via `/api/post/`

### 2. Système d'escalade
- **Opérateur 1** : 3 tentatives maximum
  - Si non résolu après 3 tentatives → Escalade vers Opérateur 2
  - Email envoyé à chaque tentative
- **Opérateur 2** : 3 tentatives maximum
  - Si non résolu après 3 tentatives → Escalade vers Opérateur 3
  - Email envoyé à chaque tentative
- **Opérateur 3** : 3 tentatives maximum
  - Dernier niveau d'escalade

### 3. Gestion des incidents
- **Accusé de réception** : L'opérateur peut accuser réception de l'incident
- **Commentaires** : Ajout de commentaires à chaque tentative
- **Résolution** : Marquage de l'incident comme résolu avec commentaire

## Installation et Configuration

### 1. Créer les opérateurs

Exécutez le script pour créer les opérateurs initiaux :

```bash
python creer_operateurs.py
```

### 2. Configurer les emails des opérateurs

1. Accédez à l'admin Django : http://127.0.0.1:8000/admin/
2. Allez dans **DHT** → **Opérateurs**
3. Modifiez les emails pour chaque opérateur avec les vrais emails

### 3. Vérifier la configuration email

Assurez-vous que les paramètres email sont corrects dans `projet/settings.py` :
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

## Utilisation

### Interface Opérateurs

**URL** : http://127.0.0.1:8000/gestion-incidents/

**Fonctionnalités** :
- Liste de tous les incidents avec filtres (statut, opérateur)
- Détails de chaque incident
- Accusé de réception
- Ajout de commentaires
- Enregistrement de tentatives
- Résolution d'incidents

### Workflow d'un incident

1. **Détection** : Un incident est créé automatiquement quand une température hors plage est détectée
2. **Notification** : Email envoyé à l'Opérateur 1
3. **Traitement** :
   - L'opérateur accède à la page de gestion
   - Accuse réception
   - Ajoute des commentaires et enregistre des tentatives
4. **Escalade** : Si 3 tentatives sans résolution → Escalade automatique vers l'opérateur suivant
5. **Résolution** : L'opérateur marque l'incident comme résolu

### Interface Admin Django

**URL** : http://127.0.0.1:8000/admin/

**Modèles disponibles** :
- **DHT11** : Données du capteur
- **Opérateurs** : Gestion des opérateurs
- **Incidents** : Gestion complète des incidents

## Modèles de données

### Operateur
- `nom` : Nom de l'opérateur
- `email` : Email pour les notifications
- `telephone` : Numéro de téléphone (optionnel)
- `ordre_escalade` : Ordre d'escalade (1, 2 ou 3)
- `actif` : Statut actif/inactif

### Incident
- `dht11` : Référence à la mesure DHT11
- `temperature` : Température qui a déclenché l'incident
- `type_incident` : "trop_bas" ou "trop_haut"
- `statut` : "ouvert", "en_cours", "resolu", "ferme"
- `operateur_actuel` : Opérateur actuellement assigné
- `operateur_initial` : Opérateur initial
- `tentatives_operateur1/2/3` : Compteurs de tentatives
- `accuse_reception` : Booléen
- `date_accuse_reception` : Date d'accusé de réception
- `commentaires` : Commentaires des opérateurs
- `date_creation` : Date de création
- `date_resolution` : Date de résolution

## API

### Détection automatique
Lors de l'ajout de données via `POST /api/post/`, le système détecte automatiquement les incidents :

```json
POST /api/post/
{
    "temp": 10.5,
    "hum": 60.0
}
```

Si `temp < 2` ou `temp > 8`, un incident est créé automatiquement.

## Exemples d'utilisation

### Créer un opérateur manuellement

```python
from DHT.models import Operateur

Operateur.objects.create(
    nom="Jean Dupont",
    email="jean.dupont@example.com",
    ordre_escalade=1,
    actif=True
)
```

### Vérifier les incidents ouverts

```python
from DHT.models import Incident

incidents_ouverts = Incident.objects.filter(statut='ouvert')
```

### Forcer l'escalade d'un incident

```python
from DHT.utils import escalader_incident

incident = Incident.objects.get(id=1)
escalader_incident(incident)
```

## Notes importantes

1. **Emails** : Les emails sont envoyés via SMTP Gmail configuré dans `settings.py`
2. **Tentatives** : Chaque action "Enregistrer tentative" incrémente le compteur
3. **Escalade automatique** : L'escalade se fait automatiquement après 3 tentatives
4. **Archivage** : Les incidents résolus restent dans la base pour consultation historique

## URLs disponibles

- `/gestion-incidents/` - Liste des incidents
- `/gestion-incidents/<id>/` - Détails d'un incident
- `/gestion-incidents/<id>/accuser-reception/` - Accuser réception
- `/gestion-incidents/<id>/commenter/` - Ajouter un commentaire
- `/gestion-incidents/<id>/traiter/` - Enregistrer une tentative
- `/gestion-incidents/<id>/resoudre/` - Résoudre un incident

