from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.liste, name="liste"),
    path("<int:pk>/lu/", views.marquer_lu, name="marquer_lu"),
    path("tout-marquer-lu/", views.marquer_toutes_lues, name="marquer_toutes_lues"),
]
