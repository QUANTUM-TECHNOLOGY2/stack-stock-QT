from django.db import models


class TypeNotification(models.TextChoices):
    NOUVELLE_RESERVATION = "NOUVELLE_RESERVATION", "Nouvelle réservation"
    NOUVELLE_COMMANDE = "NOUVELLE_COMMANDE", "Nouvelle commande"
    A_VALIDER = "A_VALIDER", "En attente de validation"
    VALIDATION = "VALIDATION", "Validation"
    REFUS = "REFUS", "Refus"
    MODIFICATION = "MODIFICATION", "Modification demandée"
    SORTIE = "SORTIE", "Sortie de stock"
    ENTREE = "ENTREE", "Entrée de stock"
    STOCK_FAIBLE = "STOCK_FAIBLE", "Stock faible / rupture"
    GARANTIE_EXPIREE = "GARANTIE_EXPIREE", "Garantie expirée"
    NOUVEAU_MATERIEL = "NOUVEAU_MATERIEL", "Nouveau matériel"
    INFO = "INFO", "Information"


class Notification(models.Model):
    utilisateur = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="notifications")
    titre = models.CharField(max_length=150)
    message = models.TextField()
    type_notification = models.CharField(max_length=30, choices=TypeNotification.choices, default=TypeNotification.INFO)
    lien = models.CharField(max_length=255, blank=True)
    lu = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-cree_le"]

    def __str__(self):
        return f"{self.titre} -> {self.utilisateur}"
