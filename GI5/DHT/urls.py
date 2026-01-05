from django.urls import path
from . import views, api

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("api/", api.Dlist, name="json"),
    path("api/post/", api.Dhtviews.as_view(), name="json"),
    path("latest/", views.latest_json, name="latest_json"),
    path("", views.dashboard, name="dashboard"),
    path("graph_temp/", views.graph_temp, name="graph_temp"),
    path("graph_hum/", views.graph_hum, name="graph_hum"),
    path("incidents/", views.incidents, name="incidents"),
    # Gestion des incidents pour opérateurs
    path("gestion-incidents/", views.liste_incidents, name="liste_incidents"),
    path("gestion-incidents/<int:incident_id>/", views.detail_incident, name="detail_incident"),
    path("gestion-incidents/<int:incident_id>/accuser-reception/", views.accuser_reception_incident, name="accuser_reception_incident"),
    path("gestion-incidents/<int:incident_id>/commenter/", views.ajouter_commentaire_incident, name="ajouter_commentaire_incident"),
    path("gestion-incidents/<int:incident_id>/resoudre/", views.resoudre_incident, name="resoudre_incident"),
    path("gestion-incidents/<int:incident_id>/traiter/", views.traiter_incident_vue, name="traiter_incident"),
]