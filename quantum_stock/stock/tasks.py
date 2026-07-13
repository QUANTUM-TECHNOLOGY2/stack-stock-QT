from celery import shared_task


@shared_task
def verifier_alertes_stock():
    """Parcourt tous les matériels actifs et notifie les responsables des stocks faibles/ruptures."""
    from accounts.models import Role, User
    from catalog.models import Materiel
    from notifications.utils import notifier

    materiels_a_risque = [
        m for m in Materiel.objects.filter(actif=True) if m.stock_faible or m.rupture_stock
    ]
    if not materiels_a_risque:
        return "Aucune alerte de stock aujourd'hui."

    destinataires = User.objects.filter(role__in=[Role.SUPER_ADMIN, Role.ADMIN, Role.MAGASINIER])
    for materiel in materiels_a_risque:
        etat = "en rupture" if materiel.rupture_stock else "en stock faible"
        for user in destinataires:
            notifier(
                utilisateur=user,
                titre="Alerte de stock quotidienne",
                message=f"{materiel.reference} ({materiel.designation}) est {etat} "
                        f"({materiel.quantite_disponible} unité(s)).",
                type_notification="STOCK_FAIBLE",
                lien=materiel.get_absolute_url(),
            )
    return f"{len(materiels_a_risque)} matériel(s) à risque notifié(s)."
