from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("titre", "utilisateur", "type_notification", "lu", "cree_le")
    list_filter = ("type_notification", "lu")
