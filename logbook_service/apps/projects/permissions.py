from rest_framework.permissions import BasePermission

from apps.projects.models import ProjectMembership

# Numeric rank for each role — higher rank includes all lower permissions.
_ROLE_RANK: dict[str, int] = {
    ProjectMembership.ROLE_VIEWER: 0,
    ProjectMembership.ROLE_EDITOR: 1,
    ProjectMembership.ROLE_ADMIN: 2,
}


def _resolve_project(obj):
    """
    Extract the related Project from a Project, Experiment, or any object
    that carries a .project FK (e.g. Entry, ProjectMembership).
    Returns None if the project cannot be resolved.
    """
    from apps.projects.models import Experiment, Project

    if isinstance(obj, Project):
        return obj
    if isinstance(obj, Experiment):
        return obj.project
    if hasattr(obj, "project") and obj.project is not None:
        return obj.project
    return None


def _get_role(user, project) -> str | None:
    """
    Return the user's active role string for the given project, or None
    if no active membership exists.
    """
    try:
        membership = ProjectMembership.objects.get(
            user=user, project=project, is_active=True
        )
        return membership.role
    except ProjectMembership.DoesNotExist:
        return None


class IsProjectMember(BasePermission):
    """
    Grants access to any active project member (Viewer, Editor, or Admin).

    For nested routes (URL contains project_pk), has_permission checks
    project-level access before the object is fetched.
    For top-level routes, defers to has_object_permission.
    """

    _required_rank: int = _ROLE_RANK[ProjectMembership.ROLE_VIEWER]

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        project_pk = view.kwargs.get("project_pk")
        if project_pk is None:
            return True  # Defer to has_object_permission for top-level routes.
        from apps.projects.models import Project

        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return False
        role = _get_role(request.user, project)
        return role is not None and _ROLE_RANK.get(role, -1) >= self._required_rank

    def has_object_permission(self, request, view, obj) -> bool:
        project = _resolve_project(obj)
        if project is None:
            return False
        role = _get_role(request.user, project)
        return role is not None and _ROLE_RANK.get(role, -1) >= self._required_rank


class IsProjectEditor(IsProjectMember):
    """
    Grants access to Editor and Admin members only.
    Use for create / update / archive actions on entries and experiments.
    """

    _required_rank: int = _ROLE_RANK[ProjectMembership.ROLE_EDITOR]


class IsProjectAdmin(IsProjectMember):
    """
    Grants access to Admin members only.
    Use for membership management, project settings, and IP-claim overrides.
    """

    _required_rank: int = _ROLE_RANK[ProjectMembership.ROLE_ADMIN]
