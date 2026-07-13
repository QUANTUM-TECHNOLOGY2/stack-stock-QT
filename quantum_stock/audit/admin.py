from django.contrib import admin

from .models import JournalActivite


@admin.register(JournalActivite)
class JournalActiviteAdmin(admin.ModelAdmin):
    list_display = ("horodatage", "utilisateur", "action", "modele", "objet_repr", "adresse_ip")
    list_filter = ("action", "modele")
    search_fields = ("objet_repr", "utilisateur__username")
    readonly_fields = [f.name for f in JournalActivite._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
