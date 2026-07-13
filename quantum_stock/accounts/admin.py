from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmailVerificationToken, User


@admin.register(User)
class QuantumUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "agence", "email_verifie", "actif_metier", "is_staff")
    list_filter = ("role", "email_verifie", "actif_metier", "agence")
    fieldsets = UserAdmin.fieldsets + (
        ("Informations QUANTUM", {
            "fields": ("role", "telephone", "agence", "service", "entreprise", "responsable",
                       "email_verifie", "actif_metier", "photo"),
        }),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "cree_le", "utilise")
    readonly_fields = ("token", "cree_le")
