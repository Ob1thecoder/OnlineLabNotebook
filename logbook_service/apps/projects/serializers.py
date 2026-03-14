from rest_framework import serializers

from apps.projects.models import Experiment, Project, ProjectMembership


class ProjectSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "is_archived",
            "owner_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner_email", "created_at", "updated_at"]


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = [
            "id",
            "project",
            "name",
            "description",
            "start_date",
            "end_date",
            "is_archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "project", "created_at", "updated_at"]


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ProjectMembership
        fields = [
            "id",
            "user_email",
            "user_full_name",
            "role",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "user_email", "user_full_name", "is_active", "created_at"]


class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=ProjectMembership.ROLE_CHOICES)
