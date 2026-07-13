from django.core.exceptions import ValidationError
from django.db import transaction

from .models import MouvementStock, TypeMouvement


@transaction.atomic
def enregistrer_mouvement(materiel, type_mouvement, quantite, utilisateur, motif="",
                           magasin_source=None, magasin_destination=None, reference_document=""):
    """
    Applique un mouvement de stock sur un matériel de façon atomique et
    conserve un historique complet (utilisé par entrées/sorties/transferts/
    ajustements et par la validation des réservations/commandes).
    """
    materiel = type(materiel).objects.select_for_update().get(pk=materiel.pk)
    quantite_avant = materiel.quantite_disponible

    if type_mouvement == TypeMouvement.ENTREE:
        materiel.quantite_disponible += abs(quantite)
    elif type_mouvement == TypeMouvement.SORTIE:
        if materiel.quantite_disponible < abs(quantite):
            raise ValidationError("Quantité disponible insuffisante pour effectuer cette sortie.")
        materiel.quantite_disponible -= abs(quantite)
    elif type_mouvement == TypeMouvement.AJUSTEMENT or type_mouvement == TypeMouvement.INVENTAIRE:
        nouvelle_quantite = materiel.quantite_disponible + quantite
        if nouvelle_quantite < 0:
            raise ValidationError("L'ajustement rendrait la quantité disponible négative.")
        materiel.quantite_disponible = nouvelle_quantite
    elif type_mouvement == TypeMouvement.TRANSFERT:
        if materiel.quantite_disponible < abs(quantite):
            raise ValidationError("Quantité disponible insuffisante pour ce transfert.")
        materiel.quantite_disponible -= abs(quantite)
        materiel.magasin = magasin_destination or materiel.magasin
    else:
        raise ValidationError("Type de mouvement inconnu.")

    materiel.save(update_fields=["quantite_disponible", "magasin"])

    mouvement = MouvementStock.objects.create(
        materiel=materiel,
        type_mouvement=type_mouvement,
        quantite=quantite,
        magasin_source=magasin_source,
        magasin_destination=magasin_destination,
        motif=motif,
        reference_document=reference_document,
        quantite_avant=quantite_avant,
        quantite_apres=materiel.quantite_disponible,
        utilisateur=utilisateur,
    )
    return mouvement
