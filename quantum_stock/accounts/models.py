import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Role(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", "Super Administrateur"
    ADMIN = "ADMIN", "Administrateur"
    RESPONSABLE = "RESPONSABLE", "Responsable hiérarchique"
    MAGASINIER = "MAGASINIER", "Magasinier"
    EMPLOYE = "EMPLOYE", "Employé"
    CLIENT_INTERNE = "CLIENT_INTERNE", "Client interne"
    CLIENT_EXTERNE = "CLIENT_EXTERNE", "Client externe"


class User(AbstractUser):
    """
    Utilisateur unique pour toute la plateforme, différencié par le champ `role`.
    """
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYE)
    telephone = models.CharField(max_length=30, blank=True)
    agence = models.ForeignKey(
        "catalog.Agence", null=True, blank=True, on_delete=models.SET_NULL, related_name="utilisateurs"
    )
    service = models.CharField(max_length=100, blank=True, help_text="Service / département (employés internes)")
    entreprise = models.CharField(max_length=150, blank=True, help_text="Entreprise (clients externes)")
    responsable = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="subordonnes", limit_choices_to={"role": Role.RESPONSABLE},
    )
    email_verifie = models.BooleanField(default=False)
    photo = models.ImageField(upload_to="utilisateurs/", null=True, blank=True)
    actif_metier = models.BooleanField(default=True, help_text="Compte activé par un administrateur")
    date_creation = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def est_administration(self):
        return self.role in {Role.SUPER_ADMIN, Role.ADMIN}

    @property
    def peut_valider(self):
        return self.role in {Role.SUPER_ADMIN, Role.ADMIN, Role.RESPONSABLE, Role.MAGASINIER}


class EmailVerificationToken(models.Model):
    """Jeton envoyé par email pour confirmer l'adresse email d'un nouvel utilisateur."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens_verification")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    cree_le = models.DateTimeField(auto_now_add=True)
    utilise = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Jeton de vérification email"
        verbose_name_plural = "Jetons de vérification email"

    def est_valide(self):
        return (not self.utilise) and (timezone.now() - self.cree_le < timedelta(hours=48))

    def __str__(self):
        return f"Jeton pour {self.user.email}"
