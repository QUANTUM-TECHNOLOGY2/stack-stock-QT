import uuid

from django.db import models
from django.urls import reverse

from workflow.models import Etape


class Reservation(models.Model):
    class Statut(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon (panier)"
        EN_ATTENTE = "EN_ATTENTE", "En attente de validation"
        MODIFICATION_DEMANDEE = "MODIFICATION_DEMANDEE", "Modification demandée"
        VALIDE = "VALIDE", "Validée"
        REFUSE = "REFUSE", "Refusée"
        ANNULE = "ANNULE", "Annulée"

    numero = models.CharField(max_length=30, unique=True, editable=False)
    demandeur = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="reservations")
    statut = models.CharField(max_length=25, choices=Statut.choices, default=Statut.BROUILLON)
    etape_courante = models.CharField(max_length=25, choices=Etape.choices, default=Etape.SOUMISSION)
    commentaire_demandeur = models.TextField(blank=True)
    date_besoin = models.DateField(null=True, blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    soumise_le = models.DateTimeField(null=True, blank=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ["-cree_le"]

    def __str__(self):
        return self.numero or f"Réservation #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"RES-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("reservations:detail", args=[self.pk])

    @property
    def nombre_articles(self):
        return self.lignes.count()

    def finaliser_validation(self):
        """Réserve physiquement la quantité de chaque ligne (quantité disponible -> réservée)."""
        for ligne in self.lignes.select_related("materiel"):
            materiel = ligne.materiel
            quantite = min(ligne.quantite, materiel.quantite_disponible)
            materiel.quantite_disponible -= quantite
            materiel.quantite_reservee += quantite
            materiel.save(update_fields=["quantite_disponible", "quantite_reservee"])


class LigneReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="lignes")
    materiel = models.ForeignKey("catalog.Materiel", on_delete=models.CASCADE, related_name="lignes_reservation")
    quantite = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Ligne de réservation"
        verbose_name_plural = "Lignes de réservation"
        unique_together = ("reservation", "materiel")

    def __str__(self):
        return f"{self.materiel.reference} x {self.quantite}"
