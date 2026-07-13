from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from catalog.models import Materiel
from workflow.services import initialiser_workflow
from .cart import PanierCommande
from .models import Commande, LigneCommande


@login_required
def panier_ajouter(request, materiel_id):
    materiel = get_object_or_404(Materiel, pk=materiel_id, actif=True)
    quantite = int(request.POST.get("quantite", 1))
    PanierCommande(request).ajouter(materiel_id, quantite)
    messages.success(request, f"{materiel.designation} ajouté au panier de commande.")
    return redirect(request.META.get("HTTP_REFERER") or "commandes:panier")


@login_required
def panier_detail(request):
    panier = PanierCommande(request)
    if request.method == "POST":
        for cle, valeur in request.POST.items():
            if cle.startswith("quantite_"):
                materiel_id = cle.replace("quantite_", "")
                try:
                    panier.definir_quantite(materiel_id, int(valeur))
                except ValueError:
                    pass
        messages.success(request, "Panier mis à jour.")
        return redirect("commandes:panier")
    lignes = list(panier.lignes())
    total = sum(l["sous_total"] for l in lignes)
    return render(request, "commandes/panier.html", {"lignes": lignes, "total": total})


@login_required
def panier_retirer(request, materiel_id):
    PanierCommande(request).retirer(materiel_id)
    messages.info(request, "Article retiré du panier.")
    return redirect("commandes:panier")


@login_required
def soumettre_commande(request):
    panier = PanierCommande(request)
    lignes = list(panier.lignes())
    if not lignes:
        messages.error(request, "Votre panier de commande est vide.")
        return redirect("commandes:panier")

    commande = Commande.objects.create(
        demandeur=request.user,
        commentaire_demandeur=request.POST.get("commentaire", ""),
        soumise_le=timezone.now(),
    )
    for ligne in lignes:
        LigneCommande.objects.create(
            commande=commande, materiel=ligne["materiel"],
            quantite=ligne["quantite"], prix_unitaire=ligne["prix_unitaire"],
        )

    initialiser_workflow(commande, request.user)
    panier.vider()

    messages.success(request, f"Commande {commande.numero} soumise avec succès.")
    return redirect("commandes:detail", pk=commande.pk)


@login_required
def mes_commandes(request):
    commandes = request.user.commandes.exclude(statut=Commande.Statut.BROUILLON)
    return render(request, "commandes/liste.html", {"commandes": commandes})


@login_required
def detail(request, pk):
    commande = get_object_or_404(Commande.objects.select_related("demandeur").prefetch_related("lignes__materiel"), pk=pk)
    from django.contrib.contenttypes.models import ContentType
    from workflow.models import EtapeValidation
    historique = EtapeValidation.objects.filter(
        content_type=ContentType.objects.get_for_model(Commande), object_id=commande.pk
    )
    return render(request, "commandes/detail.html", {"commande": commande, "historique": historique})


@login_required
def annuler(request, pk):
    commande = get_object_or_404(Commande, pk=pk, demandeur=request.user)
    if commande.statut in {Commande.Statut.EN_ATTENTE, Commande.Statut.MODIFICATION_DEMANDEE}:
        commande.statut = Commande.Statut.ANNULE
        commande.save(update_fields=["statut"])
        messages.success(request, "Commande annulée.")
    else:
        messages.error(request, "Cette commande ne peut plus être annulée.")
    return redirect("commandes:detail", pk=pk)


@login_required
def bon_de_commande_pdf(request, pk):
    commande = get_object_or_404(Commande.objects.prefetch_related("lignes__materiel"), pk=pk)

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="bon_commande_{commande.numero}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    largeur, hauteur = A4

    pdf.setFillColorRGB(0.16, 0.20, 0.38)  # bleu QUANTUM
    pdf.rect(0, hauteur - 2.5 * cm, largeur, 2.5 * cm, fill=1, stroke=0)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(2 * cm, hauteur - 1.6 * cm, "QUANTUM TECHNOLOGY - Bon de commande")

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 11)
    y = hauteur - 3.5 * cm
    pdf.drawString(2 * cm, y, f"Numéro : {commande.numero}")
    pdf.drawString(11 * cm, y, f"Date : {commande.soumise_le or commande.cree_le:%d/%m/%Y}")
    y -= 0.7 * cm
    pdf.drawString(2 * cm, y, f"Demandeur : {commande.demandeur.get_full_name() or commande.demandeur.username}")
    y -= 0.7 * cm
    pdf.drawString(2 * cm, y, f"Statut : {commande.get_statut_display()}")

    y -= 1.2 * cm
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(2 * cm, y, "Référence")
    pdf.drawString(6 * cm, y, "Désignation")
    pdf.drawString(12 * cm, y, "Qté")
    pdf.drawString(14 * cm, y, "Prix unitaire")
    pdf.drawString(17 * cm, y, "Sous-total")
    y -= 0.3 * cm
    pdf.line(2 * cm, y, largeur - 2 * cm, y)

    pdf.setFont("Helvetica", 10)
    for ligne in commande.lignes.all():
        y -= 0.6 * cm
        if y < 3 * cm:
            pdf.showPage()
            y = hauteur - 3 * cm
        pdf.drawString(2 * cm, y, ligne.materiel.reference)
        pdf.drawString(6 * cm, y, ligne.materiel.designation[:35])
        pdf.drawString(12 * cm, y, str(ligne.quantite))
        pdf.drawString(14 * cm, y, f"{ligne.prix_unitaire:.2f}")
        pdf.drawString(17 * cm, y, f"{ligne.sous_total:.2f}")

    y -= 1 * cm
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(14 * cm, y, f"Total : {commande.montant_total:.2f}")

    pdf.showPage()
    pdf.save()
    return response
