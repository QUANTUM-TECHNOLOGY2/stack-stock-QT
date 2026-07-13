def notifications_non_lues(request):
    if not request.user.is_authenticated:
        return {}
    return {
        "nb_notifications_non_lues": request.user.notifications.filter(lu=False).count(),
        "dernieres_notifications": request.user.notifications.all()[:8],
    }
