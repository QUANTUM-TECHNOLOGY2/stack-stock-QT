from celery import shared_task
from django.utils import timezone


@shared_task
def verifier_garanties_expirees():
    """Détecte les matériels dont la garantie vient d'expirer et notifie les administrateurs."""
    from accounts.models import Role, User
    from notifications.utils import notifier
    from .models import Materiel

    aujourd_hui = timezone.now().date()
    materiels = Materiel.objects.filter(garantie_fin=aujourd_hui, actif=True)
    if not materiels.exists():
        return "Aucune garantie expirée aujourd'hui."

    administrateurs = User.objects.filter(role__in=[Role.SUPER_ADMIN, Role.ADMIN])
    for materiel in materiels:
        for admin in administrateurs:
            notifier(
                utilisateur=admin,
                titre="Garantie expirée",
                message=f"La garantie du matériel {materiel.reference} ({materiel.designation}) vient d'expirer.",
                type_notification="GARANTIE_EXPIREE",
                lien=materiel.get_absolute_url(),
            )
    return f"{materiels.count()} matériel(s) notifié(s)."
