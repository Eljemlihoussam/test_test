"""
Script pour lier les opérateurs aux utilisateurs Django
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from django.contrib.auth.models import User
from DHT.models import Operateur

print("Liaison des operateurs aux utilisateurs Django...")
print("=" * 60)

# Récupérer ou créer les utilisateurs pour chaque opérateur
operateurs = Operateur.objects.filter(actif=True).order_by('ordre_escalade')

for op in operateurs:
    print(f"\nOperateur: {op.nom} ({op.email})")
    
    if op.user:
        print(f"  [DEJA LIE] Utilisateur: {op.user.username}")
        continue
    
    # Chercher un utilisateur avec le même email
    user = User.objects.filter(email=op.email).first()
    
    if not user:
        # Créer un nouvel utilisateur
        username = f"operateur{op.ordre_escalade}"
        # Vérifier si le username existe déjà
        if User.objects.filter(username=username).exists():
            username = f"operateur{op.ordre_escalade}_{op.id}"
        
        user = User.objects.create_user(
            username=username,
            email=op.email,
            password='operateur123',  # Mot de passe par défaut - À CHANGER !
            first_name=op.nom.split()[0] if op.nom.split() else op.nom,
            is_staff=False,
            is_active=True
        )
        print(f"  [CREÉ] Utilisateur cree: {username} (mot de passe: operateur123)")
    else:
        print(f"  [TROUVE] Utilisateur existant: {user.username}")
    
    # Lier l'opérateur à l'utilisateur
    op.user = user
    op.save()
    print(f"  [OK] Operateur lie a l'utilisateur {user.username}")

print("\n" + "=" * 60)
print("\n[IMPORTANT]")
print("1. Les mots de passe par defaut sont 'operateur123'")
print("2. Demandez aux operateurs de changer leur mot de passe apres la premiere connexion")
print("3. Vous pouvez creer des utilisateurs manuellement dans l'admin Django")
print("4. Puis lier les operateurs aux utilisateurs dans l'admin Django")

