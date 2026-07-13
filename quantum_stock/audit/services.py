from django.forms.models import model_to_dict

from .middleware import get_client_ip, get_current_request
from .models import JournalActivite


def _serialisable(valeurs):
    """Convertit un dict issu de model_to_dict en dict JSON-sérialisable (dates, décimaux, fichiers...)."""
    propre = {}
    for cle, valeur in valeurs.items():
        if valeur is None or isinstance(valeur, (str, int, float, bool)):
            propre[cle] = valeur
        else:
            propre[cle] = str(valeur)
    return propre


def enregistrer(action, instance=None, ancienne_valeur=None, utilisateur=None, commentaire=""):
    request = get_current_request()
    user = utilisateur or (getattr(request, "user", None) if request else None)
    if user is not None and not getattr(user, "is_authenticated", False):
        user = None

    nouvelle_valeur = None
    modele = ""
    objet_id = ""
    objet_repr = commentaire

    if instance is not None:
        modele = instance.__class__.__name__
        objet_id = str(instance.pk)
        objet_repr = commentaire or str(instance)
        try:
            nouvelle_valeur = _serialisable(model_to_dict(instance))
        except Exception:
            nouvelle_valeur = None

    JournalActivite.objects.create(
        utilisateur=user,
        action=action,
        modele=modele,
        objet_id=objet_id,
        objet_repr=objet_repr,
        ancienne_valeur=ancienne_valeur,
        nouvelle_valeur=nouvelle_valeur,
        adresse_ip=get_client_ip(request),
        navigateur=(request.META.get("HTTP_USER_AGENT", "")[:255] if request else ""),
    )
