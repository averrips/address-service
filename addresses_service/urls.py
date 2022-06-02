# isort: skip_file
from django.contrib import admin
from django.urls import include, path

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
from django.views.generic import TemplateView

from .apps.addresses.urls import router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path(
        "docs/",
        TemplateView.as_view(
            template_name="docs.html",
            extra_context={"schema_url": "/static/openapi.yaml"},
        ),
        name="redoc",
    ),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
