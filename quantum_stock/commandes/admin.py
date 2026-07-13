from django.contrib import admin

from .models import Commande, LigneCommande


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ("numero", "demandeur", "statut", "etape_courante", "cree_le")
    list_filter = ("statut", "etape_courante")
    search_fields = ("numero", "demandeur__username")
    inlines = [LigneCommandeInline]
