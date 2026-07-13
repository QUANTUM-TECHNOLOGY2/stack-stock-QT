from django import forms

from .models import Categorie, DocumentMateriel, Materiel, PhotoMateriel

INPUT = "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#D61C4E]"


class MaterielForm(forms.ModelForm):
    class Meta:
        model = Materiel
        exclude = ["reference", "code_barre_image", "qr_code", "cree_par", "cree_le", "modifie_le"]
        widgets = {
            "designation": forms.TextInput(attrs={"class": INPUT}),
            "description": forms.Textarea(attrs={"class": INPUT, "rows": 3}),
            "code_interne": forms.TextInput(attrs={"class": INPUT}),
            "numero_serie": forms.TextInput(attrs={"class": INPUT}),
            "categorie": forms.Select(attrs={"class": INPUT}),
            "marque": forms.TextInput(attrs={"class": INPUT}),
            "modele": forms.TextInput(attrs={"class": INPUT}),
            "version": forms.TextInput(attrs={"class": INPUT}),
            "couleur": forms.TextInput(attrs={"class": INPUT}),
            "etat": forms.Select(attrs={"class": INPUT}),
            "agence": forms.Select(attrs={"class": INPUT}),
            "magasin": forms.Select(attrs={"class": INPUT}),
            "fournisseur": forms.Select(attrs={"class": INPUT}),
            "date_achat": forms.DateInput(attrs={"class": INPUT, "type": "date"}),
            "garantie_fin": forms.DateInput(attrs={"class": INPUT, "type": "date"}),
            "prix_achat": forms.NumberInput(attrs={"class": INPUT}),
            "valeur": forms.NumberInput(attrs={"class": INPUT}),
            "quantite_disponible": forms.NumberInput(attrs={"class": INPUT}),
            "quantite_minimale": forms.NumberInput(attrs={"class": INPUT}),
            "quantite_maximale": forms.NumberInput(attrs={"class": INPUT}),
            "quantite_critique": forms.NumberInput(attrs={"class": INPUT}),
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ["nom", "niveau", "parent", "masque", "description"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": INPUT}),
            "niveau": forms.Select(attrs={"class": INPUT}),
            "parent": forms.Select(attrs={"class": INPUT}),
            "masque": forms.TextInput(attrs={"class": INPUT}),
            "description": forms.Textarea(attrs={"class": INPUT, "rows": 2}),
        }


class RechercheMaterielForm(forms.Form):
    q = forms.CharField(label="Recherche", required=False, widget=forms.TextInput(
        attrs={"class": INPUT, "placeholder": "Référence, désignation, n° de série..."}))
    categorie = forms.ModelChoiceField(label="Catégorie", queryset=Categorie.objects.all(), required=False,
                                        widget=forms.Select(attrs={"class": INPUT}))
    disponible = forms.BooleanField(label="Disponible uniquement", required=False)
