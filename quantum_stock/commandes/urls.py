from django.urls import path

from . import views

app_name = "commandes"

urlpatterns = [
    path("panier/", views.panier_detail, name="panier"),
    path("panier/ajouter/<int:materiel_id>/", views.panier_ajouter, name="panier_ajouter"),
    path("panier/retirer/<int:materiel_id>/", views.panier_retirer, name="panier_retirer"),
    path("soumettre/", views.soumettre_commande, name="soumettre"),
    path("mes-commandes/", views.mes_commandes, name="mes_commandes"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/annuler/", views.annuler, name="annuler"),
    path("<int:pk>/bon-pdf/", views.bon_de_commande_pdf, name="bon_pdf"),
]
