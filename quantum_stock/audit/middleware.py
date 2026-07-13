import threading

_local = threading.local()


class AuditMiddleware:
    """
    Rend la requête courante (utilisateur, IP, user-agent) accessible aux
    signaux Django exécutés en dehors du cycle requête/réponse habituel,
    afin d'alimenter le journal des activités de façon transparente.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.request = request
        try:
            response = self.get_response(request)
        finally:
            _local.request = None
        return response


def get_current_request():
    return getattr(_local, "request", None)


def get_client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
