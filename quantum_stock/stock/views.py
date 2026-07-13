from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from accounts.models import Role
from .forms import AjustementForm, MouvementForm, TransfertForm
from .models import MouvementStock, TypeMouvement
from .services import enregistrer_mouvement


def _acces_autorise(user):
    return user.role in {Role.SUPER_ADMIN, Role.ADMIN, Role.MAGASINIER}


@login_required
def historique(request):
    mouvements = MouvementStock.objects.select_related("materiel", "utilisateur").all()[:200]
    return render(request, "stock/historique.html", {"mouvements": mouvements})


@login_required
def entree(request):
    if not _acces_autorise(request.user):
        messages.error(request, "Accès réservé aux magasiniers et administrateurs.")
        return redirect("stock:historique")
    if request.method == "POST":
        form = MouvementForm(request.POST)
        if form.is_valid():
            try:
                enregistrer_mouvement(
                    materiel=form.cleaned_data["materiel"],
                    type_mouvement=TypeMouvement.ENTREE,
                    quantite=form.cleaned_data["quantite"],
                    utilisateur=request.user,
                    motif=form.cleaned_data["motif"],
                    reference_document=form.cleaned_data["reference_document"],
                )
                messages.success(request, "Entrée de stock enregistrée.")
                return redirect("stock:historique")
            except ValidationError as exc:
                messages.error(request, str(exc))
    else:
        form = MouvementForm()
    return render(request, "stock/mouvement_form.html", {"form": form, "titre": "Nouvelle entrée de stock"})


@login_required
def sortie(request):
    if not _acces_autorise(request.user):
        messages.error(request, "Accès réservé aux magasiniers et administrateurs.")
        return redirect("stock:historique")
    if request.method == "POST":
        form = MouvementForm(request.POST)
        if form.is_valid():
            try:
                enregistrer_mouvement(
                    materiel=form.cleaned_data["materiel"],
                    type_mouvement=TypeMouvement.SORTIE,
                    quantite=-form.cleaned_data["quantite"],
                    utilisateur=request.user,
                    motif=form.cleaned_data["motif"],
                    reference_document=form.cleaned_data["reference_document"],
                )
                messages.success(request, "Sortie de stock enregistrée.")
                return redirect("stock:historique")
            except ValidationError as exc:
                messages.error(request, str(exc))
    else:
        form = MouvementForm()
    return render(request, "stock/mouvement_form.html", {"form": form, "titre": "Nouvelle sortie de stock"})


@login_required
def transfert(request):
    if not _acces_autorise(request.user):
        messages.error(request, "Accès réservé aux magasiniers et administrateurs.")
        return redirect("stock:historique")
    if request.method == "POST":
        form = TransfertForm(request.POST)
        if form.is_valid():
            try:
                enregistrer_mouvement(
                    materiel=form.cleaned_data["materiel"],
                    type_mouvement=TypeMouvement.TRANSFERT,
                    quantite=-form.cleaned_data["quantite"],
                    utilisateur=request.user,
                    motif=form.cleaned_data["motif"],
                    magasin_source=form.cleaned_data["materiel"].magasin,
                    magasin_destination=form.cleaned_data["magasin_destination"],
                    reference_document=form.cleaned_data["reference_document"],
                )
                messages.success(request, "Transfert enregistré.")
                return redirect("stock:historique")
            except ValidationError as exc:
                messages.error(request, str(exc))
    else:
        form = TransfertForm()
    return render(request, "stock/mouvement_form.html", {"form": form, "titre": "Nouveau transfert"})


@login_required
def ajustement(request):
    if not _acces_autorise(request.user):
        messages.error(request, "Accès réservé aux magasiniers et administrateurs.")
        return redirect("stock:historique")
    if request.method == "POST":
        form = AjustementForm(request.POST)
        if form.is_valid():
            try:
                enregistrer_mouvement(
                    materiel=form.cleaned_data["materiel"],
                    type_mouvement=TypeMouvement.AJUSTEMENT,
                    quantite=form.cleaned_data["delta"],
                    utilisateur=request.user,
                    motif=form.cleaned_data["motif"],
                )
                messages.success(request, "Ajustement de stock enregistré.")
                return redirect("stock:historique")
            except ValidationError as exc:
                messages.error(request, str(exc))
    else:
        form = AjustementForm()
    return render(request, "stock/mouvement_form.html", {"form": form, "titre": "Ajustement de stock"})
