# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Dht11

def login_view(request):
    """Vue de connexion pour les administrateurs (accès à /admin/)"""
    if request.user.is_authenticated:
        return redirect('/admin/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/admin/')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, "login.html")

def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('dashboard')

def dashboard(request):
    return render(request, "dashboard.html")

def graph_temp(request):
    return render(request, "graph_temp.html")

def graph_hum(request):
    return render(request, "graph_hum.html")


def latest_json(request):
    last = Dht11.objects.order_by('-dt').first()
    if not last:
        return JsonResponse({"detail": "no data"}, status=404)

    # Assure-toi que last.dt est aware
    if timezone.is_naive(last.dt):
        last_dt = timezone.make_aware(last.dt, timezone=timezone.utc)
    else:
        last_dt = last.dt

    now = timezone.now()
    elapsed_minutes = int((now - last_dt).total_seconds() // 60)

    return JsonResponse({
        "temperature": last.temp,
        "humidity": last.hum,
        "minutes_since_last": elapsed_minutes,
        "timestamp": last.dt.isoformat()
    })


def incidents(request):
    # Page d'incidents (affichage front, les données viennent de /api/ via JS/HTML)
    return render(request, "incidents.html")


# ============================================================
# =============  GESTION DES INCIDENTS POUR OPÉRATEURS  ====
# ============================================================

from .models import Incident, Operateur
from .utils import traiter_incident, accuser_reception, escalader_incident
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

def get_operateur_from_user(user):
    """Récupère l'opérateur associé à un utilisateur Django"""
    if not user or not user.is_authenticated:
        return None
    try:
        return Operateur.objects.get(user=user)
    except Operateur.DoesNotExist:
        return None


def verifier_permission_modification(request, incident):
    """
    Vérifie si l'utilisateur connecté peut modifier cet incident.
    Seul l'opérateur assigné peut modifier son incident.
    Les superutilisateurs (admins) peuvent aussi modifier pour la gestion.
    """
    if not request.user.is_authenticated:
        return False, "Vous devez être connecté pour modifier un incident."
    
    # Les superutilisateurs peuvent modifier tous les incidents (pour la gestion admin)
    if request.user.is_superuser:
        return True, None
    
    operateur = get_operateur_from_user(request.user)
    if not operateur:
        return False, "Vous n'êtes pas un opérateur autorisé. Seuls les opérateurs assignés peuvent modifier leurs incidents."
    
    if incident.operateur_actuel != operateur:
        return False, f"Vous n'êtes pas autorisé à modifier cet incident. Il est assigné à {incident.operateur_actuel.nom if incident.operateur_actuel else 'un autre opérateur'} (Opérateur {incident.operateur_actuel.ordre_escalade if incident.operateur_actuel else 'N/A'}). Seul cet opérateur peut le modifier."
    
    return True, None


def liste_incidents(request):
    """Liste tous les incidents avec filtres"""
    incidents = Incident.objects.all().order_by('-date_creation')
    
    # Si l'utilisateur est un opérateur, filtrer par défaut ses incidents
    operateur_connecte = get_operateur_from_user(request.user)
    if operateur_connecte and not request.GET.get('operateur'):
        incidents = incidents.filter(operateur_actuel=operateur_connecte)
    
    # Filtres
    statut_filter = request.GET.get('statut', '')
    operateur_filter = request.GET.get('operateur', '')
    
    if statut_filter:
        incidents = incidents.filter(statut=statut_filter)
    
    if operateur_filter:
        incidents = incidents.filter(operateur_actuel_id=operateur_filter)
    
    operateurs = Operateur.objects.filter(actif=True)
    
    context = {
        'incidents': incidents,
        'operateurs': operateurs,
        'statut_filter': statut_filter,
        'operateur_filter': operateur_filter,
        'operateur_connecte': operateur_connecte,
    }
    return render(request, 'gestion_incidents/liste.html', context)


def detail_incident(request, incident_id):
    """Détails d'un incident"""
    try:
        incident = Incident.objects.get(id=incident_id)
    except Incident.DoesNotExist:
        messages.error(request, "Incident introuvable.")
        return redirect('liste_incidents')
    
    operateurs = Operateur.objects.filter(actif=True)
    operateur_connecte = get_operateur_from_user(request.user)
    peut_modifier, message_erreur = verifier_permission_modification(request, incident)
    
    context = {
        'incident': incident,
        'operateurs': operateurs,
        'operateur_connecte': operateur_connecte,
        'peut_modifier': peut_modifier,
        'message_erreur': message_erreur,
    }
    return render(request, 'gestion_incidents/detail.html', context)


@require_http_methods(["POST"])
def accuser_reception_incident(request, incident_id):
    """Accuser réception d'un incident - Seul l'opérateur assigné peut le faire"""
    try:
        incident = Incident.objects.get(id=incident_id)
        peut_modifier, message_erreur = verifier_permission_modification(request, incident)
        
        if not peut_modifier:
            messages.error(request, message_erreur)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': message_erreur}, status=403)
            return redirect('detail_incident', incident_id=incident_id)
        
        accuser_reception(incident)
        messages.success(request, f"Accusé de réception enregistré pour l'incident #{incident.id}")
    except Incident.DoesNotExist:
        messages.error(request, "Incident introuvable.")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('detail_incident', incident_id=incident_id)


@require_http_methods(["POST"])
def ajouter_commentaire_incident(request, incident_id):
    """Ajouter un commentaire à un incident - Seul l'opérateur assigné peut le faire"""
    try:
        incident = Incident.objects.get(id=incident_id)
        peut_modifier, message_erreur = verifier_permission_modification(request, incident)
        
        if not peut_modifier:
            messages.error(request, message_erreur)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': message_erreur}, status=403)
            return redirect('detail_incident', incident_id=incident_id)
        
        commentaire = request.POST.get('commentaire', '').strip()
        
        if commentaire:
            traiter_incident(incident, commentaire=commentaire)
            messages.success(request, "Commentaire ajouté avec succès.")
        else:
            messages.error(request, "Le commentaire ne peut pas être vide.")
    except Incident.DoesNotExist:
        messages.error(request, "Incident introuvable.")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('detail_incident', incident_id=incident_id)


@require_http_methods(["POST"])
def resoudre_incident(request, incident_id):
    """Résoudre un incident - Seul l'opérateur assigné peut le faire"""
    try:
        incident = Incident.objects.get(id=incident_id)
        peut_modifier, message_erreur = verifier_permission_modification(request, incident)
        
        if not peut_modifier:
            messages.error(request, message_erreur)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': message_erreur}, status=403)
            return redirect('detail_incident', incident_id=incident_id)
        
        commentaire = request.POST.get('commentaire', '').strip()
        traiter_incident(incident, commentaire=commentaire, resoudre=True)
        messages.success(request, f"Incident #{incident.id} résolu avec succès.")
    except Incident.DoesNotExist:
        messages.error(request, "Incident introuvable.")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('liste_incidents')


@require_http_methods(["POST"])
def traiter_incident_vue(request, incident_id):
    """Traiter un incident (incrémenter tentative) - Seul l'opérateur assigné peut le faire"""
    try:
        incident = Incident.objects.get(id=incident_id)
        peut_modifier, message_erreur = verifier_permission_modification(request, incident)
        
        if not peut_modifier:
            messages.error(request, message_erreur)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': message_erreur}, status=403)
            return redirect('detail_incident', incident_id=incident_id)
        
        commentaire = request.POST.get('commentaire', '').strip()
        traiter_incident(incident, commentaire=commentaire)
        
        # Vérifier si escalade nécessaire
        if incident.peut_escalader():
            escalader_incident(incident)
            messages.warning(request, f"Incident #{incident.id} escaladé vers l'opérateur suivant.")
        else:
            messages.success(request, f"Tentative enregistrée pour l'incident #{incident.id}.")
    except Incident.DoesNotExist:
        messages.error(request, "Incident introuvable.")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('detail_incident', incident_id=incident_id)