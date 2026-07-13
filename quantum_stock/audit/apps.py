from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "audit"
    verbose_name = "Journal des activités"

    def ready(self):
        import audit.signals  # noqa
