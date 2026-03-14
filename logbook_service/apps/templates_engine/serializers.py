from rest_framework import serializers

from apps.templates_engine.models import EntryTemplate, TemplateSection


class TemplateSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateSection
        fields = ["id", "title", "prompt", "is_required", "order"]
        read_only_fields = fields


class EntryTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoint — no nested sections."""

    class Meta:
        model = EntryTemplate
        fields = ["id", "name", "slug", "description", "discipline", "is_builtin", "created_at"]
        read_only_fields = fields


class EntryTemplateDetailSerializer(serializers.ModelSerializer):
    """Detail serializer with nested sections ordered by `order`."""

    sections = TemplateSectionSerializer(many=True, read_only=True)

    class Meta:
        model = EntryTemplate
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "discipline",
            "is_builtin",
            "sections",
            "created_at",
        ]
        read_only_fields = fields
