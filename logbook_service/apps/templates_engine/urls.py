from rest_framework.routers import DefaultRouter

from apps.templates_engine.views import EntryTemplateViewSet

router = DefaultRouter()
router.register(r"", EntryTemplateViewSet, basename="template")

urlpatterns = router.urls
