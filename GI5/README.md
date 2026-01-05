# Projet Django - Monitoring DHT11

Application web Django pour le monitoring de température et d'humidité avec capteur DHT11.

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## 🚀 Installation et Lancement

### 1. Activer l'environnement virtuel

**Sur Windows (PowerShell) :**
```powershell
.\venv\Scripts\Activate.ps1
```

**Sur Windows (CMD) :**
```cmd
venv\Scripts\activate.bat
```

**Sur Linux/Mac :**
```bash
source venv/bin/activate
```

### 2. Installer les dépendances

Si les dépendances ne sont pas installées :
```bash
pip install -r requirement.txt
```

### 3. Appliquer les migrations de la base de données

```bash
python manage.py migrate
```

### 4. Créer un superutilisateur (pour l'accès admin)

```bash
python manage.py createsuperuser
```

Vous devrez entrer :
- Nom d'utilisateur
- Email (optionnel)
- Mot de passe (deux fois)

### 5. Lancer le serveur de développement

```bash
python manage.py runserver
```

Le serveur sera accessible à l'adresse : **http://127.0.0.1:8000/**

## 🔐 Accès à l'application

### Page de connexion
- URL : http://127.0.0.1:8000/login/
- Utilisez les identifiants du superutilisateur créé à l'étape 4

### Dashboard principal
- URL : http://127.0.0.1:8000/
- Nécessite une authentification

### Interface Django Admin
- URL : http://127.0.0.1:8000/admin/
- Utilisez les identifiants du superutilisateur

## 📡 API Endpoints

### GET /api/
Récupère toutes les données du capteur DHT11
- Paramètres optionnels : `?start=YYYY-MM-DD&end=YYYY-MM-DD`

### POST /api/post/
Envoie de nouvelles données de température et humidité
- Body JSON : `{"temp": 25.5, "hum": 60.0}`

### GET /latest/
Récupère la dernière mesure avec le temps écoulé

## 🎯 Pages disponibles

- `/` - Dashboard principal
- `/login/` - Page de connexion
- `/logout/` - Déconnexion
- `/graph_temp/` - Graphique historique température
- `/graph_hum/` - Graphique historique humidité
- `/incidents/` - Archives des incidents
- `/admin/` - Interface d'administration Django

## ⚙️ Configuration

Les paramètres de configuration se trouvent dans `projet/settings.py` :
- Email (Gmail SMTP)
- Telegram Bot Token
- Twilio (pour les appels d'alerte)

## 🔔 Système d'alertes

L'application envoie automatiquement des alertes lorsque la température dépasse 20°C :
- Email via SMTP Gmail
- Message Telegram (si configuré)
- Appel téléphonique Twilio (si configuré)

## 📝 Notes

- La base de données SQLite (`db.sqlite3`) est créée automatiquement
- Les fichiers statiques sont servis depuis `DHT/static/`
- Les templates se trouvent dans `templates/`

