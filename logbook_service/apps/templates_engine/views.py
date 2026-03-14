from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.templates_engine.models import EntryTemplate
from apps.templates_engine.serializers import (
    EntryTemplateDetailSerializer,
    EntryTemplateListSerializer,
)


class EntryTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for the template library.

    GET /api/templates/           — list active templates
    GET /api/templates/{slug}/    — detail with nested sections

    Query params:
      ?discipline=electrical       exact match on discipline field
      ?search=circuit              case-insensitive name/description search
    """

    lookup_field = "slug"

    def get_queryset(self):
        qs = EntryTemplate.objects.filter(is_active=True)
        discipline = self.request.query_params.get("discipline")
        search = self.request.query_params.get("search")
        if discipline:
            qs = qs.filter(discipline=discipline)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        return qs

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EntryTemplateDetailSerializer
        return EntryTemplateListSerializer
