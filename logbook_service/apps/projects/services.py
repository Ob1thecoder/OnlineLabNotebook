from django.db import transaction

from apps.projects.models import Project, ProjectMembership
from apps.users.models import User


@transaction.atomic
def create_project(name: str, description: str, owner: User) -> Project:
    """
    Create a project and automatically grant the owner Admin membership.
    """
    project = Project.objects.create(name=name, description=description, owner=owner)
    ProjectMembership.objects.create(
        user=owner, project=project, role=ProjectMembership.ROLE_ADMIN
    )
    return project


def invite_member(project: Project, email: str, role: str) -> ProjectMembership:
    """
    Add an existing user to a project by email.

    - If the user has no prior membership, creates one.
    - If a previously revoked membership exists, reactivates it with the new role.
    - If the user is already an active member, raises ValidationError.
    """
    from rest_framework.exceptions import NotFound, ValidationError

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise NotFound(f"No account found for '{email}'.")

    membership, created = ProjectMembership.objects.get_or_create(
        user=user,
        project=project,
        defaults={"role": role, "is_active": True},
    )

    if not created:
        if membership.is_active:
            raise ValidationError("This user is already an active member of this project.")
        membership.role = role
        membership.is_active = True
        membership.save(update_fields=["role", "is_active"])

    return membership


def revoke_member(membership: ProjectMembership) -> ProjectMembership:
    """
    Deactivate a project membership. Does not delete the record.
    """
    membership.is_active = False
    membership.save(update_fields=["is_active"])
    return membership
