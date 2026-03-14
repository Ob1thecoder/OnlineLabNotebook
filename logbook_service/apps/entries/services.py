from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.entries.models import AuditLog, Entry, EntryVersion
from apps.projects.models import Project
from apps.users.models import User


@transaction.atomic
def create_entry(
    project: Project,
    author: User,
    title: str,
    content: str,
    summary: str = "",
    experiment=None,
    template=None,
) -> Entry:
    """
    Create an entry, its first version, and an audit log record.
    Calls full_clean() to enforce the cross-project experiment constraint.
    """
    entry = Entry(
        project=project,
        author=author,
        title=title,
        summary=summary,
        experiment=experiment,
        template=template,
    )
    entry.full_clean()
    entry.save()

    EntryVersion.objects.create(
        entry=entry,
        version_number=1,
        content=content,
        created_by=author,
    )
    AuditLog.objects.create(
        entry=entry,
        actor=author,
        action=AuditLog.ACTION_CREATED,
    )
    return entry


@transaction.atomic
def update_entry(
    entry: Entry,
    actor: User,
    content: str,
    title: str | None = None,
    summary: str | None = None,
) -> Entry:
    """
    Save a new version of an entry's content and update optional metadata fields.

    Uses select_for_update() to prevent race conditions when computing the
    next version number during concurrent auto-saves.
    Raises PermissionDenied if the entry is submitted or archived.
    """
    entry = Entry.objects.select_for_update().get(pk=entry.pk)

    if entry.status == Entry.STATUS_SUBMITTED:
        raise PermissionDenied("Submitted entries cannot be edited.")
    if entry.is_archived:
        raise PermissionDenied("Archived entries cannot be edited.")

    update_fields = []
    if title is not None and title != entry.title:
        entry.title = title
        update_fields.append("title")
    if summary is not None and summary != entry.summary:
        entry.summary = summary
        update_fields.append("summary")
    if update_fields:
        entry.save(update_fields=update_fields)

    last_version = entry.versions.order_by("-version_number").first()
    next_version_number = (last_version.version_number + 1) if last_version else 1

    EntryVersion.objects.create(
        entry=entry,
        version_number=next_version_number,
        content=content,
        created_by=actor,
    )
    AuditLog.objects.create(
        entry=entry,
        actor=actor,
        action=AuditLog.ACTION_UPDATED,
    )
    return entry


def archive_entry(entry: Entry, actor: User, force: bool = False) -> Entry:
    """
    Mark an entry as archived.

    Raises PermissionDenied if the entry carries an IP claim and force=False.
    Only an Admin should pass force=True (enforced at the view layer).
    """
    if hasattr(entry, "ip_claim") and not force:
        raise PermissionDenied(
            "This entry has an IP claim. An Admin must confirm archival."
        )
    entry.is_archived = True
    entry.save(update_fields=["is_archived"])
    AuditLog.objects.create(
        entry=entry,
        actor=actor,
        action=AuditLog.ACTION_ARCHIVED,
    )
    return entry


def submit_entry(entry: Entry, actor: User) -> Entry:
    """
    Transition an entry to 'submitted', locking it from further edits.

    Only Draft or Returned entries may be submitted.
    """
    submittable = {Entry.STATUS_DRAFT, Entry.STATUS_RETURNED}
    if entry.status not in submittable:
        raise ValidationError(
            f"Only draft or returned entries can be submitted. Current status: {entry.status}."
        )
    if entry.is_archived:
        raise PermissionDenied("Archived entries cannot be submitted.")

    entry.status = Entry.STATUS_SUBMITTED
    entry.save(update_fields=["status"])
    AuditLog.objects.create(
        entry=entry,
        actor=actor,
        action=AuditLog.ACTION_SUBMITTED,
    )
    return entry
