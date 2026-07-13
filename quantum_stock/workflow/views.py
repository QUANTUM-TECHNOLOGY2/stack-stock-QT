from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect, render

from commandes.models import Commande
from reservations.models import Reservation
from .models import Decision
from .services import traiter_etape


@login_required
def a_valider(request):
    reservations = Reservation.objects.exclude(statut__in=["VALIDE", "REFUSE", "ANNULE"])
    commandes = Commande.objects.exclude(statut__in=["VALIDE", "REFUSE", "ANNULE"])
    if not request.user.est_administration:
        reservations = [r for r in reservations if r.etape_courante in _roles_utilisateur(request.user)]
        commandes = [c for c in commandes if c.etape_courante in _roles_utilisateur(request.user)]
    return render(request, "workflow/a_valider.html", {"reservations": reservations, "commandes": commandes})


def _roles_utilisateur(user):
    from .services import ROLES_PAR_ETAPE
    return [etape for etape, roles in ROLES_PAR_ETAPE.items() if user.role in roles]


@login_required
def traiter(request, modele, pk):
    ModeleClasse = Reservation if modele == "reservation" else Commande
    objet = ModeleClasse.objects.get(pk=pk)

    if request.method == "POST":
        decision = request.POST.get("decision")
        commentaire = request.POST.get("commentaire", "")
        try:
            traiter_etape(objet, request.user, decision, commentaire)
            messages.success(request, "Décision enregistrée avec succès.")
        except PermissionDenied as exc:
            messages.error(request, str(exc))
        except ValidationError as exc:
            messages.error(request, str(exc))
    return redirect("workflow:a_valider")
