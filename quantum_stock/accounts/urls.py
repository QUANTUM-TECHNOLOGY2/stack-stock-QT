from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"

urlpatterns = [
    path("inscription/", views.inscription, name="inscription"),
    path("verifier-email/<uuid:token>/", views.verifier_email, name="verifier_email"),
    path("connexion/", views.ConnexionView.as_view(), name="login"),
    path("deconnexion/", views.deconnexion, name="logout"),
    path("profil/", views.profil, name="profil"),

    # Réinitialisation du mot de passe (vues intégrées Django, gabarits personnalisés)
    path(
        "mot-de-passe-oublie/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/mot_de_passe_oublie.html",
            email_template_name="registration/email_reinitialisation.txt",
            subject_template_name="registration/email_reinitialisation_sujet.txt",
            success_url=reverse_lazy("accounts:mot_de_passe_oublie_envoye"),
        ),
        name="mot_de_passe_oublie",
    ),
    path(
        "mot-de-passe-oublie/envoye/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/mot_de_passe_oublie_envoye.html"),
        name="mot_de_passe_oublie_envoye",
    ),
    path(
        "reinitialiser/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/mot_de_passe_reinitialiser.html",
            success_url=reverse_lazy("accounts:mot_de_passe_reinitialise"),
        ),
        name="mot_de_passe_confirmer",
    ),
    path(
        "reinitialiser/termine/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/mot_de_passe_reinitialise.html"),
        name="mot_de_passe_reinitialise",
    ),
]
