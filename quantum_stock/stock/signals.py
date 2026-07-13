from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MouvementStock


@receiver(post_save, sender=MouvementStock)
def alerter_stock_faible(sender, instance, created, **kwargs):
    if not created:
        return
    from accounts.models import Role, User
    from notifications.utils import notifier

    materiel = instance.materiel
    if materiel.rupture_stock or materiel.stock_faible:
        administrateurs = User.objects.filter(
            role__in=[Role.SUPER_ADMIN, Role.ADMIN, Role.MAGASINIER]
        )
        titre = "Rupture de stock" if materiel.rupture_stock else "Stock faible"
        for user in administrateurs:
            notifier(
                utilisateur=user,
                titre=titre,
                message=f"{materiel.reference} ({materiel.designation}) : "
                        f"{materiel.quantite_disponible} unité(s) disponible(s).",
                type_notification="STOCK_FAIBLE",
                lien=materiel.get_absolute_url(),
            )
