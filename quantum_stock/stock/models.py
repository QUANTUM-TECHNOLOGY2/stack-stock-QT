from django.db import models


class TypeMouvement(models.TextChoices):
    ENTREE = "ENTREE", "Entrée"
    SORTIE = "SORTIE", "Sortie"
    TRANSFERT = "TRANSFERT", "Transfert"
    AJUSTEMENT = "AJUSTEMENT", "Ajustement"
    INVENTAIRE = "INVENTAIRE", "Inventaire (correction)"


class MouvementStock(models.Model):
    materiel = models.ForeignKey("catalog.Materiel", on_delete=models.CASCADE, related_name="mouvements")
    type_mouvement = models.CharField(max_length=20, choices=TypeMouvement.choices)
    quantite = models.IntegerField(help_text="Positif pour une entrée, négatif pour une sortie")

    magasin_source = models.ForeignKey(
        "catalog.Magasin", null=True, blank=True, on_delete=models.SET_NULL, related_name="mouvements_sortants"
    )
    magasin_destination = models.ForeignKey(
        "catalog.Magasin", null=True, blank=True, on_delete=models.SET_NULL, related_name="mouvements_entrants"
    )

    motif = models.CharField(max_length=255, blank=True)
    reference_document = models.CharField(max_length=100, blank=True, help_text="N° bon, facture, réservation, etc.")

    quantite_avant = models.IntegerField(default=0)
    quantite_apres = models.IntegerField(default=0)

    utilisateur = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="mouvements_stock")
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ["-cree_le"]

    def __str__(self):
        return f"{self.get_type_mouvement_display()} - {self.materiel.reference} ({self.quantite:+d})"


class Inventaire(models.Model):
    class Statut(models.TextChoices):
        PLANIFIE = "PLANIFIE", "Planifié"
        EN_COURS = "EN_COURS", "En cours"
        TERMINE = "TERMINE", "Terminé"

    titre = models.CharField(max_length=150)
    magasin = models.ForeignKey("catalog.Magasin", on_delete=models.CASCADE, related_name="inventaires")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.PLANIFIE)
    date_planifiee = models.DateField()
    date_realisation = models.DateTimeField(null=True, blank=True)
    responsable = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="inventaires_geres")
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Inventaire"
        verbose_name_plural = "Inventaires"
        ordering = ["-date_planifiee"]

    def __str__(self):
        return f"{self.titre} - {self.magasin} ({self.get_statut_display()})"


class LigneInventaire(models.Model):
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE, related_name="lignes")
    materiel = models.ForeignKey("catalog.Materiel", on_delete=models.CASCADE, related_name="lignes_inventaire")
    quantite_theorique = models.IntegerField()
    quantite_comptee = models.IntegerField(null=True, blank=True)
    ecart_justifie = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ligne d'inventaire"
        verbose_name_plural = "Lignes d'inventaire"
        unique_together = ("inventaire", "materiel")

    @property
    def ecart(self):
        if self.quantite_comptee is None:
            return None
        return self.quantite_comptee - self.quantite_theorique
