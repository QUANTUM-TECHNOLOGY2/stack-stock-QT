from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("comptes/", include("accounts.urls")),
    path("materiels/", include("catalog.urls")),
    path("stock/", include("stock.urls")),
    path("reservations/", include("reservations.urls")),
    path("commandes/", include("commandes.urls")),
    path("workflow/", include("workflow.urls")),
    path("notifications/", include("notifications.urls")),
    path("audit/", include("audit.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)