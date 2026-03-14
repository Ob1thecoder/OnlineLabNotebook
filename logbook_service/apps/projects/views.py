from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.projects.models import Experiment, Project, ProjectMembership
from apps.projects.permissions import IsProjectAdmin, IsProjectEditor, IsProjectMember
from apps.projects.serializers import (
    ExperimentSerializer,
    InviteMemberSerializer,
    ProjectMembershipSerializer,
    ProjectSerializer,
)
from apps.projects.services import create_project, invite_member, revoke_member


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
        ).distinct()

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsProjectAdmin()]
        if self.action == "retrieve":
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated()]  # list, create

    def perform_create(self, serializer):
        create_project(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            owner=self.request.user,
        )


class ExperimentViewSet(viewsets.ModelViewSet):
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        return Experiment.objects.filter(
            project_id=self.kwargs["project_pk"],
            project__memberships__user=self.request.user,
            project__memberships__is_active=True,
        ).distinct()

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsProjectAdmin()]
        if self.action in ["create", "update", "partial_update"]:
            return [IsAuthenticated(), IsProjectEditor()]
        return [IsAuthenticated(), IsProjectMember()]  # list, retrieve

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        serializer.save(project=project)


class MembershipViewSet(viewsets.GenericViewSet):
    serializer_class = ProjectMembershipSerializer

    def get_queryset(self):
        return ProjectMembership.objects.filter(
            project_id=self.kwargs["project_pk"],
            project__memberships__user=self.request.user,
            project__memberships__is_active=True,
        ).distinct()

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated(), IsProjectAdmin()]

    def list(self, request, project_pk=None):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = invite_member(
            project=project,
            email=serializer.validated_data["email"],
            role=serializer.validated_data["role"],
        )
        return Response(
            ProjectMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, project_pk=None, pk=None):
        membership = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(membership, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def revoke(self, request, project_pk=None, pk=None):
        membership = get_object_or_404(self.get_queryset(), pk=pk)
        revoke_member(membership)
        return Response(status=status.HTTP_204_NO_CONTENT)
