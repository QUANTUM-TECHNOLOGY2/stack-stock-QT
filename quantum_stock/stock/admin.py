from django.contrib import admin

from .models import Inventaire, LigneInventaire, MouvementStock


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ("materiel", "type_mouvement", "quantite", "utilisateur", "cree_le")
    list_filter = ("type_mouvement", "cree_le")
    search_fields = ("materiel__reference", "materiel__designation", "reference_document")
    readonly_fields = ("quantite_avant", "quantite_apres", "cree_le")


class LigneInventaireInline(admin.TabularInline):
    model = LigneInventaire
    extra = 0


@admin.register(Inventaire)
class InventaireAdmin(admin.ModelAdmin):
    list_display = ("titre", "magasin", "statut", "date_planifiee", "responsable")
    list_filter = ("statut", "magasin")
    inlines = [LigneInventaireInline]
