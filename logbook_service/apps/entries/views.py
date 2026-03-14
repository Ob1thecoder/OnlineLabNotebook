from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.entries.models import AuditLog, Entry
from apps.entries.permissions import CanAdminEntry, CanEditEntry, CanViewEntry
from apps.entries.serializers import (
    AuditLogSerializer,
    EntryCreateSerializer,
    EntrySerializer,
    EntryUpdateSerializer,
    EntryVersionSerializer,
)
from apps.entries.services import archive_entry, create_entry, submit_entry, update_entry
from apps.projects.models import ProjectMembership
from apps.projects.permissions import _ROLE_RANK, _get_role


class EntryViewSet(viewsets.ModelViewSet):
    serializer_class = EntrySerializer

    def get_queryset(self):
        qs = (
            Entry.objects.filter(
                project__memberships__user=self.request.user,
                project__memberships__is_active=True,
            )
            .select_related("author", "project", "experiment", "template")
            .distinct()
        )
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(summary__icontains=search)
            )
        return qs

    def get_permissions(self):
        if self.action in ["update", "partial_update", "archive", "submit"]:
            return [IsAuthenticated(), CanEditEntry()]
        if self.action in ["retrieve", "versions", "audit_log"]:
            return [IsAuthenticated(), CanViewEntry()]
        return [IsAuthenticated()]  # list, create — project check done in create()

    # ------------------------------------------------------------------
    # Create — uses EntryCreateSerializer; checks project membership
    # ------------------------------------------------------------------

    def create(self, request, *args, **kwargs):
        serializer = EntryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = serializer.validated_data["project"]
        role = _get_role(request.user, project)
        if not role or _ROLE_RANK.get(role, -1) < _ROLE_RANK[ProjectMembership.ROLE_EDITOR]:
            raise PermissionDenied("You must be an Editor or Admin to create entries.")

        entry = create_entry(
            project=project,
            author=request.user,
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            summary=serializer.validated_data.get("summary", ""),
            experiment=serializer.validated_data.get("experiment"),
            template=serializer.validated_data.get("template"),
        )
        return Response(EntrySerializer(entry).data, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------
    # Update — uses EntryUpdateSerializer; creates a new EntryVersion
    # ------------------------------------------------------------------

    def update(self, request, *args, **kwargs):
        entry = self.get_object()
        serializer = EntryUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = update_entry(
            entry=entry,
            actor=request.user,
            content=serializer.validated_data["content"],
            title=serializer.validated_data.get("title"),
            summary=serializer.validated_data.get("summary"),
        )
        return Response(EntrySerializer(entry).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # Entries are never hard-deleted — use /archive/ instead.
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="Entries cannot be deleted. Use /archive/ instead.")

    # ------------------------------------------------------------------
    # Custom actions
    # ------------------------------------------------------------------

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        entry = self.get_object()
        entry = submit_entry(entry=entry, actor=request.user)
        return Response(EntrySerializer(entry).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        entry = self.get_object()
        role = _get_role(request.user, entry.project)
        # Only admins may force-archive an IP-claimed entry.
        force = _ROLE_RANK.get(role, -1) >= _ROLE_RANK[ProjectMembership.ROLE_ADMIN]
        entry = archive_entry(entry=entry, actor=request.user, force=force)
        return Response(EntrySerializer(entry).data)

    @action(detail=True, methods=["get"], url_path="versions")
    def versions(self, request, pk=None):
        entry = self.get_object()
        versions = entry.versions.order_by("version_number")
        return Response(EntryVersionSerializer(versions, many=True).data)

    @action(detail=True, methods=["get"], url_path="audit-log")
    def audit_log(self, request, pk=None):
        entry = self.get_object()
        logs = AuditLog.objects.filter(entry=entry)
        return Response(AuditLogSerializer(logs, many=True).data)
