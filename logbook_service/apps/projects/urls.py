from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.projects.views import ExperimentViewSet, MembershipViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r"", ProjectViewSet, basename="project")

experiment_list = ExperimentViewSet.as_view({"get": "list", "post": "create"})
experiment_detail = ExperimentViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

membership_list = MembershipViewSet.as_view({"get": "list", "post": "create"})
membership_detail = MembershipViewSet.as_view({"patch": "partial_update"})
membership_revoke = MembershipViewSet.as_view({"post": "revoke"})

urlpatterns = [
    *router.urls,
    path("<int:project_pk>/experiments/", experiment_list, name="experiment-list"),
    path("<int:project_pk>/experiments/<int:pk>/", experiment_detail, name="experiment-detail"),
    path("<int:project_pk>/members/", membership_list, name="membership-list"),
    path("<int:project_pk>/members/<int:pk>/", membership_detail, name="membership-detail"),
    path("<int:project_pk>/members/<int:pk>/revoke/", membership_revoke, name="membership-revoke"),
]
