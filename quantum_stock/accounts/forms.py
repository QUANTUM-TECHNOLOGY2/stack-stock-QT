from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Role, User

INPUT_CLASSES = (
    "w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-[#D61C4E] focus:border-transparent transition"
)


class InscriptionForm(UserCreationForm):
    first_name = forms.CharField(label="Prénom", widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
    last_name = forms.CharField(label="Nom", widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
    email = forms.EmailField(label="Adresse email", widget=forms.EmailInput(attrs={"class": INPUT_CLASSES}))
    telephone = forms.CharField(label="Téléphone", required=False, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "telephone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("username", "password1", "password2"):
            self.fields[name].widget.attrs["class"] = INPUT_CLASSES

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Role.EMPLOYE
        user.email_verifie = True
        user.is_active = True
        if commit:
            user.save()
        return user


class ConnexionForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES


class ProfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "telephone", "photo", "service", "entreprise"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "last_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "email": forms.EmailInput(attrs={"class": INPUT_CLASSES}),
            "telephone": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "service": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "entreprise": forms.TextInput(attrs={"class": INPUT_CLASSES}),
        }