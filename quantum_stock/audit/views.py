from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render

from accounts.models import Role
from .models import JournalActivite


def _est_admin(user):
    return user.is_authenticated and user.role in {Role.SUPER_ADMIN, Role.ADMIN}


@login_required
@user_passes_test(_est_admin, login_url="dashboard:index")
def journal(request):
    entrees = JournalActivite.objects.select_related("utilisateur").all()

    action = request.GET.get("action")
    if action:
        entrees = entrees.filter(action=action)
    modele = request.GET.get("modele")
    if modele:
        entrees = entrees.filter(modele__icontains=modele)

    paginator = Paginator(entrees, 50)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "audit/journal.html", {"page_obj": page})
