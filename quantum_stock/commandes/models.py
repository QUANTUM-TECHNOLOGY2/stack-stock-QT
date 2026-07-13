import uuid

from django.db import models
from django.urls import reverse

from workflow.models import Etape


class Commande(models.Model):
    class Statut(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon (panier)"
        EN_ATTENTE = "EN_ATTENTE", "En attente de validation"
        MODIFICATION_DEMANDEE = "MODIFICATION_DEMANDEE", "Modification demandée"
        VALIDE = "VALIDE", "Validée"
        REFUSE = "REFUSE", "Refusée"
        ANNULE = "ANNULE", "Annulée"

    numero = models.CharField(max_length=30, unique=True, editable=False)
    demandeur = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="commandes")
    statut = models.CharField(max_length=25, choices=Statut.choices, default=Statut.BROUILLON)
    etape_courante = models.CharField(max_length=25, choices=Etape.choices, default=Etape.SOUMISSION)
    commentaire_demandeur = models.TextField(blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    soumise_le = models.DateTimeField(null=True, blank=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ["-cree_le"]

    def __str__(self):
        return self.numero or f"Commande #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"CMD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("commandes:detail", args=[self.pk])

    @property
    def montant_total(self):
        return sum((ligne.sous_total for ligne in self.lignes.all()), 0)

    def finaliser_validation(self):
        """Passe chaque ligne en quantité commandée sur le matériel concerné."""
        for ligne in self.lignes.select_related("materiel"):
            materiel = ligne.materiel
            materiel.quantite_commandee += ligne.quantite
            materiel.save(update_fields=["quantite_commandee"])


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes")
    materiel = models.ForeignKey("catalog.Materiel", on_delete=models.CASCADE, related_name="lignes_commande")
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
        unique_together = ("commande", "materiel")

    def __str__(self):
        return f"{self.materiel.reference} x {self.quantite}"

    @property
    def sous_total(self):
        return self.prix_unitaire * self.quantite
