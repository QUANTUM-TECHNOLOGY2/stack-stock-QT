from django.contrib import admin

from .models import Agence, Categorie, DocumentMateriel, Fournisseur, Magasin, Materiel, PhotoMateriel


@admin.register(Agence)
class AgenceAdmin(admin.ModelAdmin):
    list_display = ("nom", "ville", "active")
    search_fields = ("nom", "ville")


@admin.register(Magasin)
class MagasinAdmin(admin.ModelAdmin):
    list_display = ("nom", "agence", "responsable", "active")
    list_filter = ("agence", "active")


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ("nom", "contact", "email", "telephone", "actif")
    search_fields = ("nom", "contact")


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "niveau", "parent", "masque")
    list_filter = ("niveau",)
    search_fields = ("nom",)


class PhotoMaterielInline(admin.TabularInline):
    model = PhotoMateriel
    extra = 1


class DocumentMaterielInline(admin.TabularInline):
    model = DocumentMateriel
    extra = 1


@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "designation", "categorie", "etat", "agence", "magasin",
        "quantite_disponible", "quantite_minimale", "actif",
    )
    list_filter = ("etat", "agence", "magasin", "categorie", "actif")
    search_fields = ("reference", "code_interne", "code_barre", "numero_serie", "designation")
    readonly_fields = ("reference", "qr_code")
    inlines = [PhotoMaterielInline, DocumentMaterielInline]
