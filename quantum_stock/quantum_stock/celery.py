import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quantum_stock.settings")

app = Celery("quantum_stock")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "verifier-alertes-stock-quotidien": {
        "task": "stock.tasks.verifier_alertes_stock",
        "schedule": crontab(hour=7, minute=0),
    },
    "verifier-garanties-expirees": {
        "task": "catalog.tasks.verifier_garanties_expirees",
        "schedule": crontab(hour=7, minute=15),
    },
}
