from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Etape(models.TextChoices):
    SOUMISSION = "SOUMISSION", "Soumission (employé / client)"
    RESPONSABLE = "RESPONSABLE", "Responsable hiérarchique"
    MAGASINIER = "MAGASINIER", "Magasinier"
    ADMINISTRATEUR = "ADMINISTRATEUR", "Administrateur"
    VALIDATION_FINALE = "VALIDATION_FINALE", "Validation finale"


class Decision(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", "En attente"
    ACCEPTE = "ACCEPTE", "Accepté"
    REFUSE = "REFUSE", "Refusé"
    MODIFICATION_DEMANDEE = "MODIFICATION_DEMANDEE", "Modification demandée"

    # Ordre des étapes après la soumission initiale
    @staticmethod
    def suite_etapes():
        return [Etape.RESPONSABLE, Etape.MAGASINIER, Etape.ADMINISTRATEUR, Etape.VALIDATION_FINALE]


class EtapeValidation(models.Model):
    """
    Historique immuable de chaque décision prise sur une réservation ou une commande.
    Lié génériquement pour être réutilisé par plusieurs modèles (Reservation, Commande...).
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    etape = models.CharField(max_length=25, choices=Etape.choices)
    decision = models.CharField(max_length=25, choices=Decision.choices, default=Decision.EN_ATTENTE)
    utilisateur = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL, related_name="validations")
    commentaire = models.TextField(blank=True)
    date_traitement = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Étape de validation"
        verbose_name_plural = "Étapes de validation"
        ordering = ["date_traitement"]

    def __str__(self):
        return f"{self.get_etape_display()} - {self.get_decision_display()}"
