from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from accounts.models import Role
from .models import Decision, Etape, EtapeValidation

# Rôle(s) autorisé(s) à traiter chaque étape du circuit
ROLES_PAR_ETAPE = {
    Etape.RESPONSABLE: {Role.RESPONSABLE, Role.SUPER_ADMIN},
    Etape.MAGASINIER: {Role.MAGASINIER, Role.SUPER_ADMIN},
    Etape.ADMINISTRATEUR: {Role.ADMIN, Role.SUPER_ADMIN},
    Etape.VALIDATION_FINALE: {Role.ADMIN, Role.SUPER_ADMIN},
}


def initialiser_workflow(objet, demandeur):
    """Enregistre la soumission initiale et positionne l'objet sur la première étape."""
    EtapeValidation.objects.create(
        content_object=objet, etape=Etape.SOUMISSION, decision=Decision.ACCEPTE,
        utilisateur=demandeur, commentaire="Soumission initiale",
    )
    objet.etape_courante = Etape.RESPONSABLE
    objet.statut = "EN_ATTENTE"
    objet.save(update_fields=["etape_courante", "statut"])
    _notifier_validateurs_etape(objet, Etape.RESPONSABLE)


def traiter_etape(objet, utilisateur, decision, commentaire=""):
    """
    Fait avancer (ou arrête) le circuit de validation d'une réservation/commande.
    `decision` doit être ACCEPTE, REFUSE ou MODIFICATION_DEMANDEE.
    """
    etape_actuelle = objet.etape_courante
    roles_autorises = ROLES_PAR_ETAPE.get(etape_actuelle, set())
    if utilisateur.role not in roles_autorises and utilisateur.role != Role.SUPER_ADMIN:
        raise PermissionDenied("Vous n'êtes pas autorisé à traiter cette étape du workflow.")

    EtapeValidation.objects.create(
        content_object=objet, etape=etape_actuelle, decision=decision,
        utilisateur=utilisateur, commentaire=commentaire,
    )

    from notifications.utils import notifier

    if decision == Decision.REFUSE:
        objet.statut = "REFUSE"
        objet.save(update_fields=["statut"])
        notifier(
            utilisateur=objet.demandeur, titre="Demande refusée",
            message=f"Votre demande {objet} a été refusée à l'étape « {etape_actuelle} ». Motif : {commentaire or 'non précisé'}.",
            type_notification="REFUS", lien=objet.get_absolute_url(),
        )
        return objet

    if decision == Decision.MODIFICATION_DEMANDEE:
        objet.statut = "MODIFICATION_DEMANDEE"
        objet.save(update_fields=["statut"])
        notifier(
            utilisateur=objet.demandeur, titre="Modification demandée",
            message=f"Une modification est demandée sur {objet} : {commentaire}",
            type_notification="MODIFICATION", lien=objet.get_absolute_url(),
        )
        return objet

    # decision == ACCEPTE -> passage à l'étape suivante
    suite = Decision.suite_etapes()
    index_actuel = suite.index(etape_actuelle)
    if index_actuel + 1 < len(suite):
        objet.etape_courante = suite[index_actuel + 1]
        objet.save(update_fields=["etape_courante"])
        _notifier_validateurs_etape(objet, objet.etape_courante)
    else:
        objet.statut = "VALIDE"
        objet.save(update_fields=["statut"])
        _finaliser(objet)
        notifier(
            utilisateur=objet.demandeur, titre="Demande validée",
            message=f"Votre demande {objet} a été entièrement validée.",
            type_notification="VALIDATION", lien=objet.get_absolute_url(),
        )
    return objet


def _notifier_validateurs_etape(objet, etape):
    from accounts.models import User
    from notifications.utils import notifier

    roles = ROLES_PAR_ETAPE.get(etape, set())
    for validateur in User.objects.filter(role__in=roles):
        notifier(
            utilisateur=validateur, titre="Nouvelle demande à valider",
            message=f"{objet} attend votre validation (étape : {etape}).",
            type_notification="A_VALIDER", lien=objet.get_absolute_url(),
        )


def _finaliser(objet):
    """Applique les effets métier une fois la validation finale obtenue (sortie de stock, etc.)."""
    finaliser = getattr(objet, "finaliser_validation", None)
    if callable(finaliser):
        finaliser()
