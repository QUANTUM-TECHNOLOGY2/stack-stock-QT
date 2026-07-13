from django import forms

from catalog.models import Magasin, Materiel

INPUT = "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#D61C4E]"


class MouvementForm(forms.Form):
    materiel = forms.ModelChoiceField(queryset=Materiel.objects.filter(actif=True), widget=forms.Select(attrs={"class": INPUT}))
    quantite = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={"class": INPUT}))
    motif = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": INPUT}))
    reference_document = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": INPUT}))


class TransfertForm(MouvementForm):
    magasin_destination = forms.ModelChoiceField(queryset=Magasin.objects.filter(active=True), widget=forms.Select(attrs={"class": INPUT}))


class AjustementForm(forms.Form):
    materiel = forms.ModelChoiceField(queryset=Materiel.objects.filter(actif=True), widget=forms.Select(attrs={"class": INPUT}))
    delta = forms.IntegerField(help_text="Positif pour ajouter, négatif pour retirer", widget=forms.NumberInput(attrs={"class": INPUT}))
    motif = forms.CharField(widget=forms.TextInput(attrs={"class": INPUT}))
