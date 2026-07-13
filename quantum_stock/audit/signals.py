from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import ActionAudit
from .services import _serialisable, enregistrer

MODELES_SUIVIS = None  # rempli au chargement pour éviter les imports circulaires trop tôt


def _modeles_suivis():
    global MODELES_SUIVIS
    if MODELES_SUIVIS is None:
        from catalog.models import Materiel
        from commandes.models import Commande
        from reservations.models import Reservation
        from stock.models import MouvementStock

        MODELES_SUIVIS = (Materiel, Commande, Reservation, MouvementStock)
    return MODELES_SUIVIS


@receiver(user_logged_in)
def log_connexion(sender, request, user, **kwargs):
    enregistrer(ActionAudit.CONNEXION, utilisateur=user, commentaire=f"Connexion de {user}")


@receiver(user_logged_out)
def log_deconnexion(sender, request, user, **kwargs):
    if user is not None:
        enregistrer(ActionAudit.DECONNEXION, utilisateur=user, commentaire=f"Déconnexion de {user}")


@receiver(pre_save)
def capturer_ancienne_valeur(sender, instance, **kwargs):
    if sender not in _modeles_suivis() or not instance.pk:
        return
    try:
        from django.forms.models import model_to_dict
        ancien = sender.objects.get(pk=instance.pk)
        instance._valeur_avant = _serialisable(model_to_dict(ancien))
    except sender.DoesNotExist:
        instance._valeur_avant = None


@receiver(post_save)
def log_creation_modification(sender, instance, created, **kwargs):
    if sender not in _modeles_suivis():
        return
    action = ActionAudit.CREATION if created else ActionAudit.MODIFICATION
    enregistrer(
        action, instance=instance,
        ancienne_valeur=None if created else getattr(instance, "_valeur_avant", None),
    )


@receiver(post_delete)
def log_suppression(sender, instance, **kwargs):
    if sender not in _modeles_suivis():
        return
    enregistrer(ActionAudit.SUPPRESSION, instance=instance, commentaire=f"Suppression de {instance}")
