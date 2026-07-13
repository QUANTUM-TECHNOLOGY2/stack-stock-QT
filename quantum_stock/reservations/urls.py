from django.urls import path

from . import views

app_name = "reservations"

urlpatterns = [
    path("panier/", views.panier_detail, name="panier"),
    path("panier/ajouter/<int:materiel_id>/", views.panier_ajouter, name="panier_ajouter"),
    path("panier/retirer/<int:materiel_id>/", views.panier_retirer, name="panier_retirer"),
    path("soumettre/", views.soumettre_reservation, name="soumettre"),
    path("mes-reservations/", views.mes_reservations, name="mes_reservations"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/annuler/", views.annuler, name="annuler"),
]
