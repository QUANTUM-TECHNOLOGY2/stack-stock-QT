from django.urls import path

from . import views

app_name = "workflow"

urlpatterns = [
    path("a-valider/", views.a_valider, name="a_valider"),
    path("traiter/<str:modele>/<int:pk>/", views.traiter, name="traiter"),
]
