from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT auth
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # App routers (wired up as apps are implemented)
    path("api/sub/plans/", include("apps.plans.urls")),
    path("api/sub/billing/", include("apps.billing.urls")),
    path("api/sub/seats/", include("apps.seats.urls")),
]
