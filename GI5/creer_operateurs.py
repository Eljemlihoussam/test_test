"""
Script pour créer les opérateurs initiaux
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from DHT.models import Operateur

# Créer les 3 opérateurs
operateurs_data = [
    {
        'nom': 'Opérateur 1',
        'email': 'ssamhou86@gmail.com',  # ⚠️ À modifier avec les vrais emails
        'telephone': '',
        'ordre_escalade': 1,
        'actif': True
    },
    {
        'nom': 'Opérateur 2',
        'email': 'eljemlihoussam@gmail.com',  # ⚠️ À modifier avec les vrais emails
        'telephone': '+33123456790',
        'ordre_escalade': 2,
        'actif': True
    },
    {
        'nom': 'Opérateur 3',
        'email': 'eljemlihoussam@gmail.com',  # ⚠️ À modifier avec les vrais emails
        'telephone': '+33123456791',
        'ordre_escalade': 3,
        'actif': True
    },
]

print("Creation des operateurs...")
for op_data in operateurs_data:
    op, created = Operateur.objects.get_or_create(
        ordre_escalade=op_data['ordre_escalade'],
        defaults=op_data
    )
    if created:
        print(f"[OK] Operateur {op_data['ordre_escalade']} cree: {op.nom} ({op.email})")
    else:
        print(f"[EXISTANT] Operateur {op_data['ordre_escalade']} existe deja: {op.nom} ({op.email})")

print("\nOperateurs crees avec succes!")
print("\n[IMPORTANT] Modifiez les emails dans l'interface admin Django pour utiliser les vrais emails.")

