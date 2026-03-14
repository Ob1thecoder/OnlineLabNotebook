from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT auth
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # App routers (wired up as apps are implemented)
    path("api/users/", include("apps.users.urls")),
    path("api/projects/", include("apps.projects.urls")),
    path("api/entries/", include("apps.entries.urls")),
    path("api/templates/", include("apps.templates_engine.urls")),
    path("api/ai/", include("apps.ai.urls")),
    path("api/export/", include("apps.export.urls")),
]
