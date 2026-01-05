# Script PowerShell pour lancer le projet Django DHT11

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lancement du projet Django DHT11" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
Write-Host "[1/4] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Vérifier les migrations
Write-Host ""
Write-Host "[2/4] Vérification des migrations..." -ForegroundColor Yellow
python manage.py migrate

# Lancer le serveur
Write-Host ""
Write-Host "[3/4] Lancement du serveur Django..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Serveur accessible sur:" -ForegroundColor Green
Write-Host "  http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver

