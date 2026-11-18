from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from catalogo.views import lista_videojuegos

urlpatterns = [
    path("admin/", admin.site.urls),
    # API REST versionada. El frontend consume /api/v1/...
    path("api/v1/", include("api.urls")),
    # Compatibilidad con enlaces antiguos del proxy/healthcheck.
    path(
        "api/",
        RedirectView.as_view(url="/api/v1/", permanent=False),
        name="api-root-redirect",
    ),
    path(
        "api/catalogo/",
        RedirectView.as_view(
            url="/api/v1/catalogo/videojuegos/", permanent=False
        ),
        name="api-catalogo-redirect",
    ),
    # Auth de Django (login/logout/password reset)
    path("cuentas/", include("django.contrib.auth.urls")),
    # Apps del proyecto
    path("cuentas/", include("cuentas.urls")),
    path("catalogo/", include("catalogo.urls")),
    path("pedidos/", include("pedidos.urls")),
    path("pagos/", include("pagos.urls")),
    path("reportes/", include("reportes.urls")),
    path("soporte/", include("soporte.urls")),
    # Raíz apunta al catálogo
    path("", lista_videojuegos, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
