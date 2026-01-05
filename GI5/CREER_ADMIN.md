# 🔐 Créer un compte administrateur

## Étapes pour créer un superutilisateur

### 1. Activer l'environnement virtuel

**PowerShell :**
```powershell
.\venv\Scripts\Activate.ps1
```

**CMD :**
```cmd
venv\Scripts\activate.bat
```

### 2. Exécuter la commande createsuperuser

```bash
python manage.py createsuperuser
```

### 3. Remplir les informations demandées

La commande va vous demander :
- **Username (nom d'utilisateur)** : Entrez un nom (ex: `admin`)
- **Email address** : Entrez un email (optionnel, peut être laissé vide)
- **Password (mot de passe)** : Entrez un mot de passe sécurisé
- **Password (again)** : Retapez le même mot de passe pour confirmation

### Exemple :

```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

## 🔑 Utiliser les identifiants

Une fois le superutilisateur créé, vous pouvez :

1. **Accéder à la page de connexion** : http://127.0.0.1:8000/login/
   - Entrez le nom d'utilisateur et le mot de passe que vous venez de créer

2. **Accéder directement à l'admin** : http://127.0.0.1:8000/admin/
   - Entrez les mêmes identifiants

## ⚠️ Important

- Les identifiants ne sont **pas stockés dans un fichier** pour des raisons de sécurité
- Vous devez **créer le compte vous-même** avec la commande `createsuperuser`
- Si vous oubliez le mot de passe, vous pouvez le réinitialiser depuis l'admin Django ou créer un nouveau superutilisateur

## 🔄 Créer plusieurs administrateurs

Vous pouvez créer autant de superutilisateurs que nécessaire en répétant la commande `createsuperuser`.

