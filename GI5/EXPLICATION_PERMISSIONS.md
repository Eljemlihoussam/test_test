# 🔐 Explication du Système de Permissions

## Comment ça fonctionne ?

### Situation actuelle

Vous voyez dans la liste des incidents :
- **Incident #5** : Assigné à "Admin (Opérateur 1)"
- **Incident #4** : Assigné à "Admin (Opérateur 1)"  
- **Incident #3** : Assigné à "Admin (Opérateur 1)"

### Pourquoi pouvez-vous modifier ?

Il y a **2 raisons possibles** :

#### 1. Vous êtes connecté en tant que superutilisateur (Admin)
- Si vous êtes connecté avec un compte **superutilisateur** (admin Django)
- Vous pouvez modifier **TOUS les incidents** pour la gestion administrative
- C'est normal et voulu pour permettre la gestion globale

#### 2. Vous êtes l'opérateur assigné
- Si vous êtes connecté avec le compte lié à "Admin (Opérateur 1)"
- Vous pouvez modifier uniquement les incidents assignés à cet opérateur

## Comment savoir qui peut modifier quoi ?

### Dans la liste des incidents

**Lignes en BLEU** = Vous pouvez modifier (incidents qui vous sont assignés)
**Lignes en BLANC** = Vous ne pouvez pas modifier (assignés à un autre opérateur)

**Colonne "Opérateur"** affiche :
- ✓ **Vert** : "Vous êtes assigné - Vous pouvez modifier"
- ✗ **Rouge** : "Assigné à un autre opérateur - Vous ne pouvez pas modifier"

**Colonne "Actions"** affiche :
- ✓ **Modifiable** (vert) : Vous pouvez modifier
- ✗ **Non modifiable** (rouge) : Vous ne pouvez pas modifier

### Dans les détails d'un incident

En haut de la page, vous verrez :
- **Si vous êtes opérateur** : "Vous êtes connecté en tant que : [Nom] (Opérateur X)"
  - ✓ Vous pouvez modifier cet incident
  - ✗ Vous ne pouvez pas modifier cet incident
  
- **Si vous êtes admin** : "🔑 Mode Admin (vous pouvez modifier tous les incidents)"

- **Si vous n'êtes pas autorisé** : Message d'alerte rouge avec explication

## Exemple concret

### Scénario 1 : Vous êtes Opérateur 1
- **Incident #5** assigné à "Admin (Opérateur 1)" → ✅ **Vous pouvez modifier**
- **Incident #4** assigné à "Admin (Opérateur 1)" → ✅ **Vous pouvez modifier**
- **Incident #3** assigné à "Admin (Opérateur 1)" → ✅ **Vous pouvez modifier**

### Scénario 2 : Vous êtes Opérateur 2
- **Incident #5** assigné à "Admin (Opérateur 1)" → ❌ **Vous NE POUVEZ PAS modifier**
- **Incident #4** assigné à "Admin (Opérateur 1)" → ❌ **Vous NE POUVEZ PAS modifier**
- **Incident #3** assigné à "Admin (Opérateur 1)" → ❌ **Vous NE POUVEZ PAS modifier**

### Scénario 3 : Vous êtes Superutilisateur (Admin)
- **Tous les incidents** → ✅ **Vous pouvez modifier** (pour la gestion)

## Comment vérifier votre statut ?

1. **Regardez en haut de la page** `/gestion-incidents/`
   - Vous verrez un message indiquant votre statut

2. **Vérifiez dans l'admin Django**
   - Allez dans **DHT** → **Opérateurs**
   - Vérifiez quel utilisateur est lié à chaque opérateur
   - Vérifiez votre compte utilisateur dans **Auth** → **Users**

## Solution : Lier votre compte à un opérateur

Si vous voulez que seul l'opérateur assigné puisse modifier :

1. **Créez un utilisateur séparé pour chaque opérateur**
   - Opérateur 1 → Utilisateur "operateur1"
   - Opérateur 2 → Utilisateur "operateur2"
   - Opérateur 3 → Utilisateur "operateur3"

2. **Liez les opérateurs aux utilisateurs dans l'admin**
   - Allez dans **DHT** → **Opérateurs**
   - Pour chaque opérateur, sélectionnez l'utilisateur correspondant

3. **Connectez-vous avec le compte opérateur**
   - Utilisez les identifiants de l'opérateur spécifique
   - Vous ne pourrez modifier que vos incidents assignés

## Résumé

- ✅ **Superutilisateur** = Peut modifier tous les incidents (gestion admin)
- ✅ **Opérateur assigné** = Peut modifier uniquement ses incidents
- ❌ **Autre opérateur** = Ne peut pas modifier (lecture seule)
- ❌ **Non connecté** = Ne peut pas modifier

Les **indicateurs visuels** (couleurs, messages) vous indiquent clairement qui peut modifier quoi !

