import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from audit.models import JournalActivite
from catalog.models import Materiel
from commandes.models import Commande
from reservations.models import Reservation
from stock.models import MouvementStock


@login_required
def index(request):
    materiels = Materiel.objects.filter(actif=True)

    kpis = {
        "nb_materiels": materiels.count(),
        "valeur_stock": materiels.aggregate(total=Sum(F("valeur") * F("quantite_disponible")))["total"] or 0,
        "reservations_attente": Reservation.objects.exclude(
            statut__in=["VALIDE", "REFUSE", "ANNULE", "BROUILLON"]
        ).count(),
        "commandes_attente": Commande.objects.exclude(
            statut__in=["VALIDE", "REFUSE", "ANNULE", "BROUILLON"]
        ).count(),
    }

    peut_voir_stock = request.user.est_administration or request.user.role == "MAGASINIER"

    evolution_labels = []
    evolution_entrees = []
    evolution_sorties = []

    if peut_voir_stock:
        alertes_stock_faible = [m for m in materiels if m.stock_faible]
        alertes_rupture = [m for m in materiels if m.rupture_stock]
        alertes_garantie = materiels.filter(
            garantie_fin__lte=timezone.now().date() + timedelta(days=30),
            garantie_fin__gte=timezone.now().date(),
        )
        plus_demandes = (
            MouvementStock.objects.filter(type_mouvement="SORTIE")
            .values("materiel__designation")
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
        )

        six_mois = timezone.now() - timedelta(days=180)
        evolution_qs = (
            MouvementStock.objects.filter(cree_le__gte=six_mois)
            .annotate(mois=TruncMonth("cree_le"))
            .values("mois", "type_mouvement")
            .annotate(total=Count("id"))
            .order_by("mois")
        )
        par_mois = {}
        for ligne in evolution_qs:
            cle = ligne["mois"].strftime("%b %Y")
            par_mois.setdefault(cle, {"ENTREE": 0, "SORTIE": 0})
            if ligne["type_mouvement"] in par_mois[cle]:
                par_mois[cle][ligne["type_mouvement"]] = ligne["total"]
        evolution_labels = list(par_mois.keys())
        evolution_entrees = [v["ENTREE"] for v in par_mois.values()]
        evolution_sorties = [v["SORTIE"] for v in par_mois.values()]
    else:
        alertes_stock_faible = []
        alertes_rupture = []
        alertes_garantie = []
        plus_demandes = []

    if request.user.est_administration:
        dernieres_activites = JournalActivite.objects.select_related("utilisateur")[:15]
    else:
        dernieres_activites = []

    mes_reservations = request.user.reservations.exclude(statut="BROUILLON").order_by("-cree_le")[:5]
    mes_commandes = request.user.commandes.exclude(statut="BROUILLON").order_by("-cree_le")[:5]

    contexte = {
        "kpis": kpis,
        "alertes_stock_faible": alertes_stock_faible[:10],
        "alertes_rupture": alertes_rupture[:10],
        "alertes_garantie": alertes_garantie[:10],
        "plus_demandes": plus_demandes,
        "dernieres_activites": dernieres_activites,
        "mes_reservations": mes_reservations,
        "mes_commandes": mes_commandes,
        "evolution_labels": json.dumps(evolution_labels),
        "evolution_entrees": json.dumps(evolution_entrees),
        "evolution_sorties": json.dumps(evolution_sorties),
        "peut_voir_stock": peut_voir_stock,
    }
    return render(request, "dashboard/index.html", contexte)