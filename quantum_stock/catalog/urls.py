from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.materiel_liste, name="materiel_liste"),
    path("ajouter/", views.materiel_creer, name="materiel_creer"),
    path("<int:pk>/", views.materiel_detail, name="materiel_detail"),
    path("<int:pk>/modifier/", views.materiel_modifier, name="materiel_modifier"),
    path("categories/", views.categorie_liste, name="categorie_liste"),
]
