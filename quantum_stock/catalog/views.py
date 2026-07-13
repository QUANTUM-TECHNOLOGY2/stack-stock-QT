from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Role
from .forms import CategorieForm, MaterielForm, RechercheMaterielForm
from .models import Categorie, Materiel


def _est_gestionnaire(user):
    return user.is_authenticated and user.role in {Role.SUPER_ADMIN, Role.ADMIN, Role.MAGASINIER}


@login_required
def materiel_liste(request):
    form = RechercheMaterielForm(request.GET or None)
    materiels = Materiel.objects.filter(actif=True).select_related("categorie", "agence", "magasin")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        categorie = form.cleaned_data.get("categorie")
        disponible = form.cleaned_data.get("disponible")
        if q:
            materiels = materiels.filter(
                Q(reference__icontains=q) | Q(designation__icontains=q) |
                Q(numero_serie__icontains=q) | Q(code_interne__icontains=q) |
                Q(marque__icontains=q)
            )
        if categorie:
            materiels = materiels.filter(categorie=categorie)
        if disponible:
            materiels = materiels.filter(quantite_disponible__gt=0)

    paginator = Paginator(materiels, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "catalog/materiel_liste.html", {"form": form, "page_obj": page})


@login_required
def materiel_detail(request, pk):
    materiel = get_object_or_404(Materiel.objects.select_related("categorie", "agence", "magasin", "fournisseur"), pk=pk)
    mouvements = materiel.mouvements.select_related("utilisateur").order_by("-cree_le")[:20]
    return render(request, "catalog/materiel_detail.html", {"materiel": materiel, "mouvements": mouvements})


@login_required
def materiel_creer(request):
    if not _est_gestionnaire(request.user):
        messages.error(request, "Vous n'avez pas les droits pour ajouter un matériel.")
        return redirect("catalog:materiel_liste")
    if request.method == "POST":
        form = MaterielForm(request.POST, request.FILES)
        if form.is_valid():
            materiel = form.save(commit=False)
            materiel.cree_par = request.user
            materiel.save()
            messages.success(request, f"Matériel {materiel.reference} créé avec succès.")
            return redirect("catalog:materiel_detail", pk=materiel.pk)
    else:
        form = MaterielForm()
    return render(request, "catalog/materiel_form.html", {"form": form, "titre": "Ajouter un matériel"})


@login_required
def materiel_modifier(request, pk):
    if not _est_gestionnaire(request.user):
        messages.error(request, "Vous n'avez pas les droits pour modifier ce matériel.")
        return redirect("catalog:materiel_liste")
    materiel = get_object_or_404(Materiel, pk=pk)
    if request.method == "POST":
        form = MaterielForm(request.POST, request.FILES, instance=materiel)
        if form.is_valid():
            form.save()
            messages.success(request, "Matériel mis à jour.")
            return redirect("catalog:materiel_detail", pk=materiel.pk)
    else:
        form = MaterielForm(instance=materiel)
    return render(request, "catalog/materiel_form.html", {"form": form, "titre": f"Modifier {materiel.reference}"})


@login_required
def categorie_liste(request):
    categories = Categorie.objects.select_related("parent").all()
    racines = categories.filter(parent__isnull=True)
    if request.method == "POST" and _est_gestionnaire(request.user):
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie créée.")
            return redirect("catalog:categorie_liste")
    else:
        form = CategorieForm()
    return render(request, "catalog/categorie_liste.html", {"racines": racines, "form": form})
