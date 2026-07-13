from django.contrib import admin

from .models import LigneReservation, Reservation


class LigneReservationInline(admin.TabularInline):
    model = LigneReservation
    extra = 0


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("numero", "demandeur", "statut", "etape_courante", "cree_le")
    list_filter = ("statut", "etape_courante")
    search_fields = ("numero", "demandeur__username")
    inlines = [LigneReservationInline]
