from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def liste(request):
    notifications = request.user.notifications.all()
    return render(request, "notifications/liste.html", {"notifications": notifications})


@login_required
def marquer_lu(request, pk):
    notification = get_object_or_404(Notification, pk=pk, utilisateur=request.user)
    notification.lu = True
    notification.save(update_fields=["lu"])
    if notification.lien:
        return redirect(notification.lien)
    return redirect("notifications:liste")


@login_required
def marquer_toutes_lues(request):
    request.user.notifications.filter(lu=False).update(lu=True)
    return redirect("notifications:liste")
