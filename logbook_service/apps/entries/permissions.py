from apps.projects.permissions import IsProjectAdmin, IsProjectEditor, IsProjectMember

# Semantic aliases for entry-level access control.
# All permission logic is resolved via Entry.project → ProjectMembership.

CanViewEntry = IsProjectMember   # Viewer, Editor, Admin
CanEditEntry = IsProjectEditor   # Editor, Admin
CanAdminEntry = IsProjectAdmin   # Admin only
