from django.db import models


class ActionAudit(models.TextChoices):
    CONNEXION = "CONNEXION", "Connexion"
    DECONNEXION = "DECONNEXION", "Déconnexion"
    CREATION = "CREATION", "Création"
    MODIFICATION = "MODIFICATION", "Modification"
    SUPPRESSION = "SUPPRESSION", "Suppression"
    VALIDATION = "VALIDATION", "Validation"
    REFUS = "REFUS", "Refus"
    ENTREE_STOCK = "ENTREE_STOCK", "Entrée de stock"
    SORTIE_STOCK = "SORTIE_STOCK", "Sortie de stock"
    RESERVATION = "RESERVATION", "Réservation"
    COMMANDE = "COMMANDE", "Commande"


class JournalActivite(models.Model):
    utilisateur = models.ForeignKey(
        "accounts.User", null=True, on_delete=models.SET_NULL, related_name="journal_activites"
    )
    action = models.CharField(max_length=30, choices=ActionAudit.choices)
    modele = models.CharField(max_length=100, blank=True, help_text="Nom du modèle concerné")
    objet_id = models.CharField(max_length=50, blank=True)
    objet_repr = models.CharField(max_length=255, blank=True)

    ancienne_valeur = models.JSONField(null=True, blank=True)
    nouvelle_valeur = models.JSONField(null=True, blank=True)

    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    navigateur = models.CharField(max_length=255, blank=True)

    horodatage = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entrée du journal d'activité"
        verbose_name_plural = "Journal des activités"
        ordering = ["-horodatage"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["modele"]),
            models.Index(fields=["horodatage"]),
        ]

    def __str__(self):
        return f"[{self.horodatage:%d/%m/%Y %H:%M}] {self.utilisateur} - {self.get_action_display()} - {self.objet_repr}"
