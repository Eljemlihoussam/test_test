from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from django.db.models import Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
from . import models

@admin.register(models.Dht11)
class Dht11Admin(admin.ModelAdmin):
    list_display = ('id', 'temp', 'hum', 'dt', 'status_badge', 'view_graphs_link', 'edit_link')
    list_filter = ('dt',)
    search_fields = ('temp', 'hum')
    readonly_fields = ('dt', 'status_badge', 'statistics_display')
    date_hierarchy = 'dt'
    ordering = ('-dt',)
    
    fieldsets = (
        ('Données du capteur', {
            'fields': ('temp', 'hum', 'dt')
        }),
        ('Statistiques', {
            'fields': ('statistics_display', 'status_badge'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Affiche un badge de statut selon la température"""
        if obj.temp is None:
            return format_html('<span style="color: #6b7280;">N/A</span>')
        elif obj.temp < 2:
            return format_html(
                '<span style="background: #0ea5e9; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold;">Alerte basse</span>'
            )
        elif obj.temp > 20:
            return format_html(
                '<span style="background: #dc2626; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold;">Alerte haute</span>'
            )
        else:
            return format_html(
                '<span style="background: #16a34a; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold;">Normal</span>'
            )
    status_badge.short_description = 'Statut'
    
    def view_graphs_link(self, obj):
        """Lien vers les graphiques"""
        return format_html(
            '<a href="/admin/DHT/dht11/graphs/" style="color: #2563eb; font-weight: bold;">📊 Voir graphiques</a>'
        )
    view_graphs_link.short_description = 'Graphiques'
    
    def edit_link(self, obj):
        """Lien pour éditer l'enregistrement"""
        if obj.id:
            return format_html(
                '<a href="/admin/DHT/dht11/{}/change/" style="color: #16a34a; font-weight: bold;">✏️ Modifier</a>',
                obj.id
            )
        return "-"
    edit_link.short_description = 'Actions'
    
    def statistics_display(self, obj):
        """Affiche les statistiques"""
        if obj.id is None:
            return "Enregistrez d'abord pour voir les statistiques"
        
        # Statistiques des 24 dernières heures
        last_24h = timezone.now() - timedelta(hours=24)
        recent_data = models.Dht11.objects.filter(dt__gte=last_24h)
        
        if recent_data.exists():
            avg_temp = recent_data.aggregate(Avg('temp'))['temp__avg']
            avg_hum = recent_data.aggregate(Avg('hum'))['hum__avg']
            max_temp = recent_data.aggregate(Max('temp'))['temp__max']
            min_temp = recent_data.aggregate(Min('temp'))['temp__min']
            
            return format_html(
                '<div style="padding: 10px; background: #f3f4f6; border-radius: 8px;">'
                '<strong>Statistiques (24h):</strong><br>'
                f'Température moyenne: {avg_temp:.1f}°C<br>'
                f'Température max: {max_temp:.1f}°C<br>'
                f'Température min: {min_temp:.1f}°C<br>'
                f'Humidité moyenne: {avg_hum:.1f}%'
                '</div>'
            )
        return "Pas de données récentes"
    statistics_display.short_description = 'Statistiques'
    
    def get_urls(self):
        """Ajoute des URLs personnalisées pour les graphiques"""
        urls = super().get_urls()
        custom_urls = [
            path('graphs/', self.admin_site.admin_view(self.graphs_view), name='DHT_dht11_graphs'),
        ]
        return custom_urls + urls
    
    def graphs_view(self, request):
        """Vue personnalisée pour afficher les graphiques dans l'admin"""
        context = {
            **self.admin_site.each_context(request),
            'title': 'Graphiques DHT11',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request, None),
        }
        return render(request, 'admin/dht11_graphs.html', context)
    
    actions = ['reset_temperature', 'reset_humidity']
    
    def reset_temperature(self, request, queryset):
        """Action pour réinitialiser la température"""
        count = queryset.update(temp=None)
        self.message_user(request, f'{count} température(s) réinitialisée(s).')
    reset_temperature.short_description = "Réinitialiser la température des sélections"
    
    def reset_humidity(self, request, queryset):
        """Action pour réinitialiser l'humidité"""
        count = queryset.update(hum=None)
        self.message_user(request, f'{count} humidité(s) réinitialisée(s).')
    reset_humidity.short_description = "Réinitialiser l'humidité des sélections"


@admin.register(models.Operateur)
class OperateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'ordre_escalade', 'actif', 'user_linked')
    list_filter = ('actif', 'ordre_escalade')
    search_fields = ('nom', 'email', 'user__username')
    ordering = ('ordre_escalade',)
    fieldsets = (
        ('Informations', {
            'fields': ('nom', 'email', 'telephone', 'ordre_escalade', 'actif')
        }),
        ('Authentification', {
            'fields': ('user',),
            'description': 'Liez cet opérateur à un utilisateur Django pour permettre la connexion et la gestion des permissions.'
        }),
    )
    
    def user_linked(self, obj):
        """Affiche si l'opérateur est lié à un utilisateur"""
        if obj.user:
            return format_html(
                '<span style="color: #16a34a; font-weight: bold;">✓ {}</span>',
                obj.user.username
            )
        return format_html('<span style="color: #dc2626;">✗ Non lié</span>')
    user_linked.short_description = 'Utilisateur lié'


@admin.register(models.Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_incident_badge', 'temperature', 'statut_badge', 'operateur_actuel', 'date_creation', 'tentatives_display')
    list_filter = ('statut', 'type_incident', 'date_creation', 'operateur_actuel')
    search_fields = ('id', 'temperature', 'commentaires')
    readonly_fields = ('date_creation', 'date_modification', 'tentatives_display', 'statut_badge', 'type_incident_badge')
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('dht11', 'temperature', 'type_incident_badge', 'statut_badge', 'date_creation', 'date_modification')
        }),
        ('Gestion opérateurs', {
            'fields': ('operateur_actuel', 'operateur_initial', 'tentatives_display')
        }),
        ('Résolution', {
            'fields': ('date_resolution', 'accuse_reception', 'date_accuse_reception', 'commentaires')
        }),
    )
    
    def type_incident_badge(self, obj):
        if obj.type_incident == 'trop_bas':
            return format_html('<span style="background: #0ea5e9; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold;">Trop basse</span>')
        else:
            return format_html('<span style="background: #dc2626; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold;">Trop haute</span>')
    type_incident_badge.short_description = 'Type'
    
    def statut_badge(self, obj):
        colors = {
            'ouvert': ('#fef3c7', '#92400e'),
            'en_cours': ('#dbeafe', '#1e40af'),
            'resolu': ('#d1fae5', '#065f46'),
            'ferme': ('#e5e7eb', '#374151'),
        }
        bg, fg = colors.get(obj.statut, ('#e5e7eb', '#374151'))
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 10px; border-radius: 12px; font-weight: bold;">{}</span>',
            bg, fg, obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'
    
    def tentatives_display(self, obj):
        return format_html(
            'Op1: {} | Op2: {} | Op3: {}',
            obj.tentatives_operateur1,
            obj.tentatives_operateur2,
            obj.tentatives_operateur3
        )
    tentatives_display.short_description = 'Tentatives'