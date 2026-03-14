"""
Tests for apps.entries.models.

Coverage:
  Entry:
    TC-ENT-001  creation with required fields only
    TC-ENT-002  creation with optional experiment and template
    TC-ENT-003  __str__ returns title
    TC-ENT-004  __str__ falls back to "Entry <pk>" when title is empty
    TC-ENT-005  default status is 'draft'
    TC-ENT-006  default is_archived is False
    TC-ENT-007  clean() passes when experiment.project == entry.project
    TC-ENT-008  clean() raises ValidationError when experiment.project != entry.project
    TC-ENT-009  clean() skips cross-project check when experiment is None
    TC-ENT-010  status choices constants

  EntryVersion:
    TC-EVR-001  creation happy path
    TC-EVR-002  __str__
    TC-EVR-003  unique_together (entry, version_number)
    TC-EVR-004  cascade-delete when entry is deleted

  AuditLog:
    TC-ALG-001  create() works on a new record
    TC-ALG-002  __str__
    TC-ALG-003  save() on an existing record raises PermissionError
    TC-ALG-004  delete() always raises PermissionError
    TC-ALG-005  actor FK is nullable (system actions)
    TC-ALG-006  entry FK uses PROTECT (cannot delete entry with logs)
    TC-ALG-007  all ACTION_ constants have expected string values

  CommentThread:
    TC-CTH-001  creation and __str__
    TC-CTH-002  is_resolved defaults to False
    TC-CTH-003  resolved_at is nullable

  Comment:
    TC-CMT-001  creation and __str__

  IPClaim:
    TC-IPC-001  creation and __str__
    TC-IPC-002  OneToOne — second claim on same entry raises IntegrityError
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError

from apps.entries.models import (
    AuditLog,
    Comment,
    CommentThread,
    Entry,
    EntryVersion,
    IPClaim,
)


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntry:
    def test_create_minimal(self, project, user):
        """TC-ENT-001: Entry is created with only the mandatory fields."""
        e = Entry.objects.create(project=project, author=user, title="Minimal")
        assert e.pk is not None
        assert e.experiment is None
        assert e.template is None

    def test_create_with_experiment_and_template(
        self, project, experiment, user, entry_template
    ):
        """TC-ENT-002: Entry accepts optional experiment and template."""
        e = Entry.objects.create(
            project=project,
            experiment=experiment,
            author=user,
            template=entry_template,
            title="Full Entry",
        )
        assert e.experiment == experiment
        assert e.template == entry_template

    def test_str_returns_title(self, entry):
        """TC-ENT-003: __str__ returns the entry title."""
        assert str(entry) == entry.title

    def test_str_fallback_when_no_title(self, project, user, db):
        """TC-ENT-004: __str__ returns 'Entry <pk>' when title is blank."""
        e = Entry.objects.create(project=project, author=user, title="")
        assert str(e) == f"Entry {e.pk}"

    def test_default_status_is_draft(self, entry):
        """TC-ENT-005: Status defaults to 'draft'."""
        assert entry.status == Entry.STATUS_DRAFT

    def test_default_is_archived_false(self, entry):
        """TC-ENT-006: is_archived defaults to False."""
        assert entry.is_archived is False

    def test_status_choices_constants(self):
        """TC-ENT-010: Status constant values are correct strings."""
        assert Entry.STATUS_DRAFT == "draft"
        assert Entry.STATUS_SUBMITTED == "submitted"
        assert Entry.STATUS_UNDER_REVIEW == "under_review"
        assert Entry.STATUS_APPROVED == "approved"
        assert Entry.STATUS_RETURNED == "returned"

    def test_clean_passes_same_project(self, entry_with_experiment):
        """TC-ENT-007: clean() raises nothing when experiment.project matches entry.project."""
        entry_with_experiment.clean()  # must not raise

    def test_clean_raises_cross_project_experiment(
        self, project, other_project, user, db
    ):
        """TC-ENT-008: clean() raises ValidationError when the experiment belongs to a different project."""
        from apps.projects.models import Experiment

        other_exp = Experiment.objects.create(
            project=other_project, name="Foreign Experiment"
        )
        e = Entry(project=project, experiment=other_exp, author=user, title="Bad Entry")
        with pytest.raises(ValidationError, match="same project"):
            e.clean()

    def test_clean_skips_check_when_no_experiment(self, project, user, db):
        """TC-ENT-009: clean() is a no-op when experiment is None."""
        e = Entry(project=project, author=user, title="No Exp")
        e.clean()  # must not raise


# ---------------------------------------------------------------------------
# EntryVersion
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntryVersion:
    def test_create_version(self, entry, user):
        """TC-EVR-001: EntryVersion is created and linked to entry."""
        ev = EntryVersion.objects.create(
            entry=entry, version_number=1, content="v1 content", created_by=user
        )
        assert ev.pk is not None
        assert ev.entry == entry
        assert ev.version_number == 1

    def test_str(self, entry, user, db):
        """TC-EVR-002: __str__ is '<entry title> v<version_number>'."""
        ev = EntryVersion.objects.create(
            entry=entry, version_number=1, content="body", created_by=user
        )
        assert str(ev) == f"{entry} v1"

    def test_unique_together_entry_version_number(self, entry, user, db):
        """TC-EVR-003: Duplicate (entry, version_number) raises IntegrityError."""
        EntryVersion.objects.create(
            entry=entry, version_number=1, content="first", created_by=user
        )
        with pytest.raises(IntegrityError):
            EntryVersion.objects.create(
                entry=entry, version_number=1, content="second", created_by=user
            )

    def test_same_version_number_different_entries(self, project, user, db):
        """TC-EVR-003b: version_number=1 may exist on two different entries."""
        e1 = Entry.objects.create(project=project, author=user, title="E1")
        e2 = Entry.objects.create(project=project, author=user, title="E2")
        ev1 = EntryVersion.objects.create(
            entry=e1, version_number=1, content="A", created_by=user
        )
        ev2 = EntryVersion.objects.create(
            entry=e2, version_number=1, content="B", created_by=user
        )
        assert ev1.pk != ev2.pk

    def test_cascade_delete_with_entry(self, entry, user, db):
        """TC-EVR-004: EntryVersion is deleted when its parent Entry is deleted."""
        ev = EntryVersion.objects.create(
            entry=entry, version_number=1, content="body", created_by=user
        )
        evid = ev.pk
        entry.delete()
        assert not EntryVersion.objects.filter(pk=evid).exists()


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAuditLog:
    def test_create_new_record(self, entry, user):
        """TC-ALG-001: AuditLog.objects.create() succeeds for a new record."""
        log = AuditLog.objects.create(
            entry=entry, actor=user, action=AuditLog.ACTION_CREATED
        )
        assert log.pk is not None

    def test_str(self, entry, user, db):
        """TC-ALG-002: __str__ is '<entry> — <action>'."""
        log = AuditLog.objects.create(
            entry=entry, actor=user, action=AuditLog.ACTION_SUBMITTED
        )
        assert str(log) == f"{entry} — {AuditLog.ACTION_SUBMITTED}"

    def test_save_on_existing_record_raises(self, entry, user, db):
        """TC-ALG-003: Calling save() on a persisted AuditLog raises PermissionError."""
        log = AuditLog.objects.create(
            entry=entry, actor=user, action=AuditLog.ACTION_CREATED
        )
        log.message = "tampered"
        with pytest.raises(PermissionError, match="immutable"):
            log.save()

    def test_delete_raises_permission_error(self, entry, user, db):
        """TC-ALG-004: Calling delete() on an AuditLog raises PermissionError."""
        log = AuditLog.objects.create(
            entry=entry, actor=user, action=AuditLog.ACTION_CREATED
        )
        with pytest.raises(PermissionError):
            log.delete()

    def test_actor_nullable(self, entry, db):
        """TC-ALG-005: actor may be None for system-generated events."""
        log = AuditLog.objects.create(
            entry=entry, actor=None, action=AuditLog.ACTION_EXPORTED
        )
        assert log.actor is None

    def test_entry_fk_is_protected(self, entry, user, db):
        """TC-ALG-006: Deleting an Entry that has AuditLog records raises ProtectedError."""
        AuditLog.objects.create(entry=entry, actor=user, action=AuditLog.ACTION_CREATED)
        with pytest.raises(ProtectedError):
            entry.delete()

    def test_action_choices_constants(self):
        """TC-ALG-007: All ACTION_ constants have the expected string values."""
        assert AuditLog.ACTION_CREATED == "created"
        assert AuditLog.ACTION_UPDATED == "updated"
        assert AuditLog.ACTION_SUBMITTED == "submitted"
        assert AuditLog.ACTION_APPROVED == "approved"
        assert AuditLog.ACTION_RETURNED == "returned"
        assert AuditLog.ACTION_ARCHIVED == "archived"
        assert AuditLog.ACTION_IP_CLAIMED == "ip_claimed"
        assert AuditLog.ACTION_EXPORTED == "exported"
        assert AuditLog.ACTION_COMMENTED == "commented"

    def test_message_optional(self, entry, user, db):
        """message field may be blank."""
        log = AuditLog.objects.create(
            entry=entry, actor=user, action=AuditLog.ACTION_ARCHIVED, message=""
        )
        assert log.message == ""


# ---------------------------------------------------------------------------
# CommentThread
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCommentThread:
    def test_create_and_str(self, entry, user):
        """TC-CTH-001: CommentThread is created; __str__ includes entry_id and created_by_id."""
        thread = CommentThread.objects.create(entry=entry, created_by=user)
        assert thread.pk is not None
        assert str(thread) == f"Thread on entry {entry.pk} by {user.pk}"

    def test_is_resolved_default_false(self, entry, user, db):
        """TC-CTH-002: is_resolved defaults to False."""
        thread = CommentThread.objects.create(entry=entry, created_by=user)
        assert thread.is_resolved is False

    def test_resolved_at_nullable(self, entry, user, db):
        """TC-CTH-003: resolved_at is None by default."""
        thread = CommentThread.objects.create(entry=entry, created_by=user)
        assert thread.resolved_at is None

    def test_anchor_fields_optional(self, entry, user, db):
        """anchor_start and anchor_end may be blank."""
        thread = CommentThread.objects.create(
            entry=entry, created_by=user, anchor_start="", anchor_end=""
        )
        assert thread.anchor_start == ""


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestComment:
    def test_create_and_str(self, entry, user, db):
        """TC-CMT-001: Comment is created inside a thread; __str__ includes pk and author_id."""
        thread = CommentThread.objects.create(entry=entry, created_by=user)
        comment = Comment.objects.create(thread=thread, author=user, body="Hello")
        assert comment.pk is not None
        assert str(comment) == f"Comment {comment.pk} by {user.pk}"


# ---------------------------------------------------------------------------
# IPClaim
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestIPClaim:
    def test_create_and_str(self, entry, user):
        """TC-IPC-001: IPClaim is created; __str__ includes entry_id and claimant_id."""
        claim = IPClaim.objects.create(
            entry=entry, claimant=user, novelty_description="Novel idea"
        )
        assert claim.pk is not None
        assert str(claim) == f"IP claim on entry {entry.pk} by {user.pk}"

    def test_one_to_one_prevents_second_claim(self, entry, user, other_user, db):
        """TC-IPC-002: A second IPClaim on the same entry raises IntegrityError."""
        IPClaim.objects.create(
            entry=entry, claimant=user, novelty_description="First claim"
        )
        with pytest.raises(IntegrityError):
            IPClaim.objects.create(
                entry=entry, claimant=other_user, novelty_description="Second claim"
            )
