from rest_framework.routers import DefaultRouter

from apps.entries.views import EntryViewSet

router = DefaultRouter()
router.register(r"", EntryViewSet, basename="entry")

urlpatterns = router.urls
