from django.contrib import admin

from .models import EtapeValidation


@admin.register(EtapeValidation)
class EtapeValidationAdmin(admin.ModelAdmin):
    list_display = ("content_object", "etape", "decision", "utilisateur", "date_traitement")
    list_filter = ("etape", "decision")
    readonly_fields = ("date_traitement",)
