@echo off
echo ========================================
echo   Lancement du projet Django DHT11
echo ========================================
echo.

REM Activer l'environnement virtuel
echo [1/4] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier les migrations
echo.
echo [2/4] Vérification des migrations...
python manage.py migrate

REM Lancer le serveur
echo.
echo [3/4] Lancement du serveur Django...
echo.
echo ========================================
echo   Serveur accessible sur:
echo   http://127.0.0.1:8000/
echo ========================================
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

python manage.py runserver

pause

