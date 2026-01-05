# 🚨 Escalade Automatique après 3 Incidents en Continu

## Nouvelle Fonctionnalité

Le système escalade maintenant automatiquement **si 3 incidents sont créés en continu** (successivement), même s'ils sont créés rapidement.

## Fonctionnement

### Détection des incidents en continu

1. **Fenêtre de temps** : Les incidents créés dans les **10 dernières minutes** sont considérés comme "en continu"

2. **Comptage automatique** : À chaque création d'incident :
   - Le système compte le nombre d'incidents du même type créés dans les 10 dernières minutes
   - Si **3 incidents ou plus** sont détectés → Escalade automatique

3. **Incrémentation des tentatives** :
   - 1 tentative automatique est ajoutée à l'opérateur actuel
   - Un commentaire est ajouté : "[Escalade automatique] X incident(s) créé(s) en continu. Tentative automatique ajoutée."

4. **Escalade immédiate** :
   - Si l'opérateur a déjà 2 tentatives → La 3ème tentative déclenche l'escalade
   - L'incident est immédiatement escaladé vers l'opérateur suivant
   - Tous les opérateurs reçoivent un email de notification

## Exemple de Scénario

### Scénario 1 : 3 incidents créés rapidement

**5:53 PM** : Incident #6 créé (Température trop haute 20°C)
- Assigné à Opérateur 1
- Tentatives Op1: 0/3

**5:54 PM** : Incident #7 créé (Température trop haute 26°C)
- Assigné à Opérateur 1 (même incident réutilisé)
- Tentatives Op1: 0/3
- **Compteur incidents continus : 2**

**5:55 PM** : Incident #8 créé (Température trop haute 27°C)
- Assigné à Opérateur 1
- **Compteur incidents continus : 3** ✅
- **→ Tentative automatique ajoutée**
- Tentatives Op1: 1/3

**5:56 PM** : Incident #9 créé (Température trop haute 27°C)
- **Compteur incidents continus : 4**
- **→ Tentative automatique ajoutée**
- Tentatives Op1: 2/3

**5:57 PM** : Incident #10 créé (Température trop haute 30°C)
- **Compteur incidents continus : 5**
- **→ Tentative automatique ajoutée**
- Tentatives Op1: 3/3 ✅
- **→ ESCALADE AUTOMATIQUE vers Opérateur 2** 🚀

## Avantages

1. **Réactivité** : Escalade immédiate si problème persistant
2. **Automatique** : Pas besoin d'attendre 30 minutes
3. **Double système** : 
   - Escalade basée sur le temps (30 min) → Pour incidents non traités
   - Escalade basée sur le nombre (3 incidents) → Pour incidents répétés

## Configuration

### Modifier la fenêtre de temps

Par défaut, les incidents créés dans les **10 dernières minutes** sont considérés comme "en continu".

Pour modifier cette valeur, changez dans `DHT/utils.py` :
```python
dix_minutes = timezone.now() - timedelta(minutes=10)  # Changez 10 par la valeur souhaitée
```

### Modifier le seuil d'escalade

Par défaut, l'escalade se déclenche après **3 incidents**.

Pour modifier cette valeur, changez dans `DHT/utils.py` :
```python
if incidents_continus >= 3:  # Changez 3 par la valeur souhaitée
```

## Vérification

Pour voir les incidents qui seront escaladés :

1. **Dans l'admin Django** : Vérifiez les incidents avec leurs tentatives
2. **Dans les commentaires** : Recherchez "[Escalade automatique] X incident(s) créé(s) en continu"
3. **Dans les emails** : Les opérateurs reçoivent une notification lors de l'escalade

## Notes importantes

1. **Comptage par type** : Seuls les incidents du même type (trop_bas ou trop_haut) sont comptés ensemble
2. **Incidents ouverts uniquement** : Seuls les incidents avec statut "ouvert" ou "en_cours" sont comptés
3. **Double protection** : Le système combine :
   - Escalade basée sur le temps (30 min sans action)
   - Escalade basée sur le nombre (3 incidents en continu)
4. **Tentatives cumulatives** : Les tentatives s'accumulent jusqu'à 3, puis escalade

## Résumé

✅ **3 incidents créés en continu** → 1 tentative automatique
✅ **6 incidents créés en continu** → 2 tentatives automatiques  
✅ **9 incidents créés en continu** → 3 tentatives → **ESCALADE AUTOMATIQUE**

Le système est maintenant plus réactif et escalade automatiquement en cas de problème persistant !

