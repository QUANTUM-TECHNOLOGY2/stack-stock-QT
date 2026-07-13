import io
import uuid

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# ------------------------------------------------------------------
# Organisation
# ------------------------------------------------------------------
class Agence(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    adresse = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Agence"
        verbose_name_plural = "Agences"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Magasin(models.Model):
    nom = models.CharField(max_length=150)
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name="magasins")
    responsable = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="magasins_geres"
    )
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Magasin"
        verbose_name_plural = "Magasins"
        unique_together = ("nom", "agence")
        ordering = ["agence__nom", "nom"]

    def __str__(self):
        return f"{self.nom} ({self.agence.nom})"


class Fournisseur(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    contact = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


# ------------------------------------------------------------------
# Hiérarchie de catégories : Catégorie > Sous-catégorie > Famille >
# Sous-famille > Type > Classe (structure arborescente unique, flexible)
# ------------------------------------------------------------------
class NiveauCategorie(models.TextChoices):
    CATEGORIE = "CATEGORIE", "Catégorie"
    SOUS_CATEGORIE = "SOUS_CATEGORIE", "Sous-catégorie"
    FAMILLE = "FAMILLE", "Famille"
    SOUS_FAMILLE = "SOUS_FAMILLE", "Sous-famille"
    TYPE = "TYPE", "Type"
    CLASSE = "CLASSE", "Classe"


class Categorie(models.Model):
    nom = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, blank=True)
    niveau = models.CharField(max_length=20, choices=NiveauCategorie.choices, default=NiveauCategorie.CATEGORIE)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="enfants"
    )
    masque = models.CharField(
        max_length=50, blank=True,
        help_text="Masque utilisé pour générer automatiquement la référence des matériels de ce nœud",
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        unique_together = ("nom", "parent")
        ordering = ["niveau", "nom"]

    def __str__(self):
        chemin = [self.nom]
        p = self.parent
        while p:
            chemin.append(p.nom)
            p = p.parent
        return " / ".join(reversed(chemin))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def chemin_complet(self):
        return str(self)


# ------------------------------------------------------------------
# Matériel
# ------------------------------------------------------------------
class EtatMateriel(models.TextChoices):
    NEUF = "NEUF", "Neuf"
    BON = "BON", "Bon état"
    MOYEN = "MOYEN", "État moyen"
    DEFECTUEUX = "DEFECTUEUX", "Défectueux"
    HORS_SERVICE = "HORS_SERVICE", "Hors service"
    REFORME = "REFORME", "Réformé"


class Materiel(models.Model):
    # Identification
    reference = models.CharField(max_length=60, unique=True, editable=False)
    code_interne = models.CharField(max_length=60, unique=True)
    code_barre = models.CharField(max_length=60, unique=True, blank=True)
    qr_code = models.ImageField(upload_to="materiels/qrcodes/", blank=True, null=True)
    code_barre_image = models.ImageField(upload_to="materiels/codesbarres/", blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True)

    # Description
    designation = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="materiels")
    marque = models.CharField(max_length=100, blank=True)
    modele = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=50, blank=True)
    couleur = models.CharField(max_length=50, blank=True)
    etat = models.CharField(max_length=20, choices=EtatMateriel.choices, default=EtatMateriel.NEUF)

    # Localisation
    agence = models.ForeignKey(Agence, on_delete=models.PROTECT, related_name="materiels")
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT, related_name="materiels")
    fournisseur = models.ForeignKey(Fournisseur, null=True, blank=True, on_delete=models.SET_NULL, related_name="materiels")

    # Achat / valorisation
    date_achat = models.DateField(null=True, blank=True)
    garantie_fin = models.DateField(null=True, blank=True, verbose_name="Fin de garantie")
    prix_achat = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valeur = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Valeur actuelle / comptable")

    # Quantités
    quantite_disponible = models.PositiveIntegerField(default=0)
    quantite_reservee = models.PositiveIntegerField(default=0)
    quantite_commandee = models.PositiveIntegerField(default=0)
    quantite_minimale = models.PositiveIntegerField(default=1)
    quantite_maximale = models.PositiveIntegerField(default=100)
    quantite_critique = models.PositiveIntegerField(default=2)

    photo_principale = models.ImageField(upload_to="materiels/photos/", blank=True, null=True)

    actif = models.BooleanField(default=True)
    cree_par = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL, related_name="materiels_crees")
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Matériel"
        verbose_name_plural = "Matériels"
        ordering = ["-cree_le"]
        indexes = [
            models.Index(fields=["designation"]),
            models.Index(fields=["reference"]),
            models.Index(fields=["numero_serie"]),
        ]

    def __str__(self):
        return f"{self.reference} - {self.designation}"

    def get_absolute_url(self):
        return reverse("catalog:materiel_detail", args=[self.pk])

    # -- État de stock --------------------------------------------------
    @property
    def quantite_totale(self):
        return self.quantite_disponible + self.quantite_reservee + self.quantite_commandee

    @property
    def stock_faible(self):
        return 0 < self.quantite_disponible <= self.quantite_minimale

    @property
    def rupture_stock(self):
        return self.quantite_disponible <= 0

    @property
    def stock_critique(self):
        return self.quantite_disponible <= self.quantite_critique

    def save(self, *args, **kwargs):
        if not self.reference:
            prefixe = (self.categorie.masque or self.categorie.nom[:3]).upper()
            self.reference = f"{prefixe}-{uuid.uuid4().hex[:8].upper()}"
        if not self.code_barre:
            self.code_barre = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)
        self._generer_qr_code()

    def _generer_qr_code(self):
        """Génère (une seule fois) le QR code encodant la référence du matériel."""
        if self.qr_code:
            return
        try:
            import qrcode
            from django.core.files.base import ContentFile

            qr_img = qrcode.make(f"MATERIEL:{self.reference}")
            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG")
            self.qr_code.save(f"{self.reference}.png", ContentFile(buffer.getvalue()), save=False)
            Materiel.objects.filter(pk=self.pk).update(qr_code=self.qr_code.name)
        except Exception:
            # La génération de QR code ne doit jamais bloquer la sauvegarde du matériel
            pass


class PhotoMateriel(models.Model):
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="materiels/photos/")
    legende = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Photo de matériel"
        verbose_name_plural = "Photos de matériel"


class DocumentMateriel(models.Model):
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE, related_name="documents")
    fichier = models.FileField(upload_to="materiels/documents/")
    nom = models.CharField(max_length=150)
    ajoute_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Document de matériel"
        verbose_name_plural = "Documents de matériel"
