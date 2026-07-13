from django.conf import settings
from django.core.mail import send_mail

from .models import Notification


def notifier(utilisateur, titre, message, type_notification="INFO", lien="", envoyer_email=True):
    """
    Crée une notification interne pour l'utilisateur et lui envoie, si activé,
    un email correspondant (comme requis par le cahier des charges).
    """
    notification = Notification.objects.create(
        utilisateur=utilisateur,
        titre=titre,
        message=message,
        type_notification=type_notification,
        lien=lien,
    )
    if envoyer_email and utilisateur.email:
        try:
            send_mail(
                subject=f"QUANTUM TECHNOLOGY - {titre}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[utilisateur.email],
                fail_silently=True,
            )
        except Exception:
            pass
    return notification
