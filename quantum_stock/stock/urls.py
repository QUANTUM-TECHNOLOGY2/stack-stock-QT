from django.urls import path

from . import views

app_name = "stock"

urlpatterns = [
    path("", views.historique, name="historique"),
    path("entree/", views.entree, name="entree"),
    path("sortie/", views.sortie, name="sortie"),
    path("transfert/", views.transfert, name="transfert"),
    path("ajustement/", views.ajustement, name="ajustement"),
]
