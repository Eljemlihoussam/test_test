"""
Script de test pour vérifier l'API et les données DHT11
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from DHT.models import Dht11
from django.utils import timezone

print("=" * 50)
print("Test des données DHT11")
print("=" * 50)

# Compter les données
total_count = Dht11.objects.count()
print(f"\nNombre total d'enregistrements: {total_count}")

if total_count == 0:
    print("\n⚠️  Aucune donnée dans la base de données!")
    print("Pour ajouter des données de test, exécutez:")
    print("python manage.py shell")
    print(">>> from DHT.models import Dht11")
    print(">>> from django.utils import timezone")
    print(">>> Dht11.objects.create(temp=25.5, hum=60.0)")
    print(">>> Dht11.objects.create(temp=20.0, hum=55.0)")
else:
    print(f"\n[OK] {total_count} enregistrement(s) trouve(s)")
    
    # Afficher les 5 derniers
    print("\n5 derniers enregistrements:")
    print("-" * 50)
    for obj in Dht11.objects.all().order_by('-dt')[:5]:
        print(f"ID: {obj.id} | Temp: {obj.temp}°C | Hum: {obj.hum}% | Date: {obj.dt}")
    
    # Tester l'API
    print("\n" + "=" * 50)
    print("Test de l'API")
    print("=" * 50)
    print("\nPour tester l'API, ouvrez dans votre navigateur:")
    print("http://127.0.0.1:8000/api/")
    print("\nOu avec curl:")
    print("curl http://127.0.0.1:8000/api/")

print("\n" + "=" * 50)

