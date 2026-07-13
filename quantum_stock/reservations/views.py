from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from catalog.models import Materiel
from notifications.utils import notifier
from workflow.services import initialiser_workflow
from .cart import Panier
from .models import LigneReservation, Reservation


@login_required
def panier_ajouter(request, materiel_id):
    materiel = get_object_or_404(Materiel, pk=materiel_id, actif=True)
    quantite = int(request.POST.get("quantite", 1))
    panier = Panier(request)
    panier.ajouter(materiel_id, quantite)
    messages.success(request, f"{materiel.designation} ajouté au panier de réservation.")
    return redirect(request.META.get("HTTP_REFERER") or "reservations:panier")


@login_required
def panier_detail(request):
    panier = Panier(request)
    if request.method == "POST":
        for cle, valeur in request.POST.items():
            if cle.startswith("quantite_"):
                materiel_id = cle.replace("quantite_", "")
                try:
                    panier.definir_quantite(materiel_id, int(valeur))
                except ValueError:
                    pass
        messages.success(request, "Panier mis à jour.")
        return redirect("reservations:panier")
    return render(request, "reservations/panier.html", {"lignes": list(panier.lignes()), "total": len(panier)})


@login_required
def panier_retirer(request, materiel_id):
    Panier(request).retirer(materiel_id)
    messages.info(request, "Article retiré du panier.")
    return redirect("reservations:panier")


@login_required
def soumettre_reservation(request):
    panier = Panier(request)
    lignes = list(panier.lignes())
    if not lignes:
        messages.error(request, "Votre panier de réservation est vide.")
        return redirect("reservations:panier")

    commentaire = request.POST.get("commentaire", "")
    date_besoin = request.POST.get("date_besoin") or None

    reservation = Reservation.objects.create(
        demandeur=request.user,
        commentaire_demandeur=commentaire,
        date_besoin=date_besoin,
        soumise_le=timezone.now(),
    )
    for ligne in lignes:
        LigneReservation.objects.create(reservation=reservation, materiel=ligne["materiel"], quantite=ligne["quantite"])

    initialiser_workflow(reservation, request.user)
    panier.vider()

    messages.success(request, f"Réservation {reservation.numero} soumise avec succès. Elle suit maintenant le circuit de validation.")
    return redirect("reservations:detail", pk=reservation.pk)


@login_required
def mes_reservations(request):
    reservations = request.user.reservations.exclude(statut=Reservation.Statut.BROUILLON)
    return render(request, "reservations/liste.html", {"reservations": reservations})


@login_required
def detail(request, pk):
    reservation = get_object_or_404(Reservation.objects.select_related("demandeur").prefetch_related("lignes__materiel"), pk=pk)
    from workflow.models import EtapeValidation
    from django.contrib.contenttypes.models import ContentType
    historique = EtapeValidation.objects.filter(
        content_type=ContentType.objects.get_for_model(Reservation), object_id=reservation.pk
    )
    return render(request, "reservations/detail.html", {"reservation": reservation, "historique": historique})


@login_required
def annuler(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, demandeur=request.user)
    if reservation.statut in {Reservation.Statut.EN_ATTENTE, Reservation.Statut.MODIFICATION_DEMANDEE}:
        reservation.statut = Reservation.Statut.ANNULE
        reservation.save(update_fields=["statut"])
        messages.success(request, "Réservation annulée.")
    else:
        messages.error(request, "Cette réservation ne peut plus être annulée.")
    return redirect("reservations:detail", pk=pk)
