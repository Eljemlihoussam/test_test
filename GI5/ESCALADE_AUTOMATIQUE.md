# ⏰ Système d'Escalade Automatique

## Problème résolu

Les incidents n'étaient pas escaladés car les tentatives restaient à 0 (personne n'enregistrait de tentatives manuellement).

## Solution : Escalade automatique basée sur le temps

### Fonctionnement

Le système escalade maintenant automatiquement les incidents **même si personne n'enregistre de tentatives** :

1. **Délai de 30 minutes** : Si un incident n'a pas été traité depuis 30 minutes
   - Une tentative automatique est ajoutée
   - Un commentaire est ajouté : "[Escalade automatique] Aucune action depuis X minutes"

2. **Après 3 tentatives automatiques** (90 minutes sans action) :
   - L'incident est automatiquement escaladé vers l'opérateur suivant
   - Tous les opérateurs reçoivent un email de notification

3. **Escalade complète** :
   - Opérateur 1 → 90 minutes sans action → Escalade vers Opérateur 2
   - Opérateur 2 → 90 minutes sans action → Escalade vers Opérateur 3
   - Opérateur 3 → 90 minutes sans action → Reste avec Opérateur 3 (dernier niveau)

## Utilisation

### Escalade automatique lors de la création de données

L'escalade est vérifiée automatiquement à chaque fois qu'une nouvelle donnée est envoyée via `/api/post/`.

### Commande manuelle

Vous pouvez aussi exécuter manuellement la commande d'escalade :

```bash
python manage.py escalader_incidents
```

**Options :**
- `--delai-minutes` : Délai en minutes avant d'incrémenter une tentative (défaut: 30)

**Exemple :**
```bash
# Escalade avec délai de 15 minutes
python manage.py escalader_incidents --delai-minutes 15
```

### Automatisation (cron/tâche planifiée)

Pour automatiser l'escalade, configurez une tâche planifiée :

**Windows (Task Scheduler) :**
- Créez une tâche qui exécute toutes les 15 minutes :
  ```
  python C:\Users\Houssam\Documents\GI5\GI5\manage.py escalader_incidents
  ```

**Linux (cron) :**
```bash
# Exécuter toutes les 15 minutes
*/15 * * * * cd /chemin/vers/projet && python manage.py escalader_incidents
```

## Exemple de timeline

### Incident créé à 5:53 PM

- **5:53 PM** : Incident créé, assigné à Opérateur 1
- **6:23 PM** (30 min) : 1ère tentative automatique ajoutée
- **6:53 PM** (60 min) : 2ème tentative automatique ajoutée
- **7:23 PM** (90 min) : 3ème tentative automatique ajoutée → **Escalade vers Opérateur 2**
- **7:53 PM** (30 min avec Op2) : 1ère tentative automatique Op2
- **8:23 PM** (60 min avec Op2) : 2ème tentative automatique Op2
- **8:53 PM** (90 min avec Op2) : 3ème tentative automatique Op2 → **Escalade vers Opérateur 3**

## Configuration

### Modifier le délai

Le délai par défaut est de **30 minutes**. Pour le modifier :

1. **Dans le code** : Modifiez `delai_minutes=30` dans `DHT/utils.py` (fonction `verifier_escalade_automatique`)
2. **Via la commande** : Utilisez `--delai-minutes` avec la commande

### Désactiver l'escalade automatique

Si vous voulez désactiver l'escalade automatique et ne compter que les tentatives manuelles :

1. Commentez l'appel à `verifier_escalade_automatique` dans `DHT/api.py`
2. Les opérateurs devront enregistrer manuellement leurs tentatives

## Vérification

Pour voir les incidents qui seront escaladés :

```bash
python manage.py escalader_incidents --delai-minutes 30
```

La commande affichera :
- Les tentatives automatiques ajoutées
- Les incidents escaladés
- Un résumé des actions

## Notes importantes

1. **Tentatives automatiques** : Sont ajoutées dans les commentaires avec le préfixe "[Escalade automatique]"
2. **Emails** : Tous les opérateurs reçoivent un email lors de l'escalade
3. **Tentatives manuelles** : Sont toujours comptées en plus des tentatives automatiques
4. **Délai** : Le délai est calculé depuis la dernière modification de l'incident

