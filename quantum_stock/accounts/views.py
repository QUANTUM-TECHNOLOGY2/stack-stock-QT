from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from .forms import ConnexionForm, InscriptionForm, ProfilForm
from .models import EmailVerificationToken, User


def _envoyer_email_verification(request, user):
    token = EmailVerificationToken.objects.create(user=user)
    lien = request.build_absolute_uri(reverse("accounts:verifier_email", args=[token.token]))
    message = render_to_string("registration/email_verification.txt", {"user": user, "lien": lien})
    send_mail(
        subject="QUANTUM TECHNOLOGY - Vérifiez votre adresse email",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def inscription(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            _envoyer_email_verification(request, user)
            messages.success(
                request,
                "Compte créé avec succès ! Un email de vérification vous a été envoyé, "
                "veuillez cliquer sur le lien reçu avant de vous connecter.",
            )
            return redirect("accounts:login")
    else:
        form = InscriptionForm()
    return render(request, "registration/inscription.html", {"form": form})


def verifier_email(request, token):
    verif = get_object_or_404(EmailVerificationToken, token=token)
    if verif.est_valide():
        verif.utilise = True
        verif.save(update_fields=["utilise"])
        verif.user.email_verifie = True
        verif.user.save(update_fields=["email_verifie"])
        messages.success(request, "Votre adresse email a bien été vérifiée. Vous pouvez maintenant vous connecter.")
    else:
        messages.error(request, "Ce lien de vérification est invalide ou expiré.")
    return redirect("accounts:login")


class ConnexionView(LoginView):
    template_name = "registration/connexion.html"
    authentication_form = ConnexionForm

    def form_valid(self, form):
        user = form.get_user()
        if not user.actif_metier:
            messages.error(self.request, "Votre compte a été désactivé. Contactez un administrateur.")
            return redirect("accounts:login")
        return super().form_valid(form)


@login_required
def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect("accounts:login")


@login_required
def profil(request):
    if request.method == "POST":
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect("accounts:profil")
    else:
        form = ProfilForm(instance=request.user)
    return render(request, "registration/profil.html", {"form": form})
