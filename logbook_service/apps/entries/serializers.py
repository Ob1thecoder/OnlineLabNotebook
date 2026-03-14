from rest_framework import serializers

from apps.entries.models import AuditLog, Entry, EntryVersion
from apps.projects.models import Experiment, Project
from apps.templates_engine.models import EntryTemplate


class EntrySerializer(serializers.ModelSerializer):
    """Read serializer — used for list, retrieve, and action responses."""

    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = Entry
        fields = [
            "id",
            "project",
            "experiment",
            "template",
            "title",
            "summary",
            "status",
            "is_archived",
            "author_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class EntryCreateSerializer(serializers.Serializer):
    """Write serializer for creating a new entry with its first version."""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    experiment = serializers.PrimaryKeyRelatedField(
        queryset=Experiment.objects.all(), required=False, allow_null=True
    )
    template = serializers.PrimaryKeyRelatedField(
        queryset=EntryTemplate.objects.all(), required=False, allow_null=True
    )
    title = serializers.CharField(max_length=255)
    summary = serializers.CharField(required=False, allow_blank=True, default="")
    content = serializers.CharField(help_text="Initial rich-text content for version 1.")


class EntryUpdateSerializer(serializers.Serializer):
    """Write serializer for updating an existing entry (creates a new version)."""

    title = serializers.CharField(max_length=255, required=False)
    summary = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(help_text="New rich-text content — always creates a version.")


class EntryVersionSerializer(serializers.ModelSerializer):
    """Read-only serializer for version history."""

    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = EntryVersion
        fields = ["id", "version_number", "content", "created_by_email", "created_at"]
        read_only_fields = fields


class AuditLogSerializer(serializers.ModelSerializer):
    """Read-only serializer for the append-only audit trail."""

    actor_email = serializers.SerializerMethodField()

    def get_actor_email(self, obj) -> str:
        return obj.actor.email if obj.actor else "system"

    class Meta:
        model = AuditLog
        fields = ["id", "action", "message", "actor_email", "created_at"]
        read_only_fields = fields
