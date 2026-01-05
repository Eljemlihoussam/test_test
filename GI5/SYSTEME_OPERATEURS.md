# 🔐 Système de Gestion des Opérateurs

## Fonctionnalités implémentées

### 1. Envoi d'emails à tous les opérateurs
✅ **Lors de la création d'un incident**, tous les opérateurs actifs reçoivent un email de notification
✅ **Lors de l'escalade**, tous les opérateurs sont notifiés du changement d'assignation

### 2. Permissions et restrictions
✅ **Seul l'opérateur assigné** peut modifier son incident
✅ **Vérification automatique** des permissions avant chaque action
✅ **Messages d'erreur clairs** si l'utilisateur n'est pas autorisé

### 3. Authentification des opérateurs
✅ **Lien entre Operateur et User Django** pour l'authentification
✅ **Filtrage automatique** : chaque opérateur voit ses incidents par défaut
✅ **Interface adaptée** selon l'opérateur connecté

## Configuration

### 1. Lier les opérateurs aux utilisateurs Django

Exécutez le script pour créer et lier les utilisateurs :

```bash
python lier_operateurs_users.py
```

Ce script :
- Crée des utilisateurs Django pour chaque opérateur (s'ils n'existent pas)
- Lie les opérateurs aux utilisateurs
- Génère des mots de passe par défaut : `operateur123`

### 2. Créer manuellement les utilisateurs (recommandé)

1. Allez dans l'admin Django : http://127.0.0.1:8000/admin/
2. Créez des utilisateurs dans **Auth** → **Users**
3. Pour chaque opérateur, créez un utilisateur avec :
   - Username : `operateur1`, `operateur2`, `operateur3`
   - Email : L'email de l'opérateur
   - Mot de passe : Choisissez un mot de passe sécurisé
4. Dans **DHT** → **Opérateurs**, liez chaque opérateur à son utilisateur

## Utilisation

### Connexion d'un opérateur

1. Allez sur : http://127.0.0.1:8000/login/
2. Connectez-vous avec les identifiants de l'opérateur
3. Accédez à : http://127.0.0.1:8000/gestion-incidents/

### Fonctionnalités par opérateur

**Chaque opérateur peut :**
- ✅ Voir tous les incidents (mais filtrés par défaut sur ses incidents)
- ✅ Modifier uniquement ses incidents assignés
- ✅ Accuser réception de ses incidents
- ✅ Ajouter des commentaires à ses incidents
- ✅ Enregistrer des tentatives pour ses incidents
- ✅ Résoudre ses incidents

**Restrictions :**
- ❌ Ne peut pas modifier les incidents assignés à d'autres opérateurs
- ❌ Voit un message d'erreur clair s'il essaie de modifier un incident non assigné

## Workflow

### 1. Création d'un incident
- Un incident est créé automatiquement (température hors plage 2-8°C)
- **Tous les opérateurs** reçoivent un email de notification
- L'incident est assigné à l'Opérateur 1

### 2. Traitement par l'Opérateur 1
- L'Opérateur 1 se connecte
- Voit l'incident dans sa liste (filtrée automatiquement)
- Peut modifier, commenter, résoudre l'incident
- Après 3 tentatives sans résolution → Escalade automatique

### 3. Escalade vers Opérateur 2
- L'incident est réassigné à l'Opérateur 2
- **Tous les opérateurs** reçoivent un email de notification
- L'Opérateur 1 ne peut plus modifier l'incident
- Seul l'Opérateur 2 peut maintenant modifier l'incident

### 4. Et ainsi de suite...

## Emails envoyés

### Contenu de l'email
- ID de l'incident
- Température mesurée
- Type d'incident (trop basse/trop haute)
- Date de détection
- Statut
- Opérateur assigné
- Lien direct vers l'incident

### Destinataires
- **Création d'incident** : Tous les opérateurs actifs
- **Escalade** : Tous les opérateurs actifs
- **Chaque opérateur** reçoit l'information même s'il n'est pas assigné

## Sécurité

### Permissions
- Vérification côté serveur (pas seulement côté client)
- Messages d'erreur HTTP 403 si tentative non autorisée
- Logs des actions pour traçabilité

### Authentification
- Utilisation du système d'authentification Django standard
- Sessions sécurisées
- Possibilité de changer les mots de passe

## Interface utilisateur

### Liste des incidents
- Filtrage automatique par opérateur connecté
- Possibilité de voir tous les incidents avec le filtre
- Indication claire de l'opérateur connecté

### Détails d'un incident
- Message d'alerte si l'utilisateur n'est pas autorisé
- Boutons d'action masqués si pas autorisé
- Indication claire de qui peut modifier l'incident

## Exemple d'utilisation

1. **Opérateur 1 se connecte**
   - Voit ses incidents assignés
   - Peut modifier ses incidents

2. **Opérateur 2 se connecte**
   - Voit ses incidents assignés (s'il en a)
   - Ne peut pas modifier les incidents de l'Opérateur 1
   - Voit un message d'erreur s'il essaie

3. **Après escalade**
   - L'incident est réassigné à l'Opérateur 2
   - L'Opérateur 1 ne peut plus le modifier
   - L'Opérateur 2 peut maintenant le modifier

## Notes importantes

1. **Mots de passe** : Changez les mots de passe par défaut après la première connexion
2. **Emails** : Vérifiez que les emails sont correctement configurés dans `settings.py`
3. **Permissions** : Les vérifications sont faites côté serveur, impossible de contourner
4. **Audit** : Toutes les actions sont tracées dans les commentaires et dates de modification

