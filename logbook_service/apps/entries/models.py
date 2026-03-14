from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.projects.models import Experiment, Project
from apps.templates_engine.models import EntryTemplate, TemplateSection


class Entry(models.Model):
    """
    Logical entry within a project/experiment.
    """

    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_UNDER_REVIEW = "under_review"
    STATUS_APPROVED = "approved"
    STATUS_RETURNED = "returned"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_UNDER_REVIEW, "Under review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_RETURNED, "Returned"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entries",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    template = models.ForeignKey(
        EntryTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entries",
    )

    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "entries_entry"
        ordering = ["-created_at"]

    def clean(self) -> None:
        if self.experiment_id and self.project_id:
            if self.experiment.project_id != self.project_id:
                raise ValidationError(
                    "The experiment must belong to the same project as this entry."
                )

    def __str__(self) -> str:
        return self.title or f"Entry {self.pk}"


class EntryVersion(models.Model):
    """
    Immutable snapshot of an entry at a point in time.

    NOTE: version_number must be assigned by the service layer using
    select_for_update() on the parent Entry to prevent race conditions
    during concurrent auto-saves. See apps/entries/services.py.
    """

    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.PositiveIntegerField()

    # For Phase 1 we keep a single rich-text payload; later phases
    # can add structured sections if needed.
    content = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entry_versions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "entries_entryversion"
        ordering = ["entry", "-version_number"]
        unique_together = ("entry", "version_number")

    def __str__(self) -> str:
        return f"{self.entry} v{self.version_number}"


class AuditLog(models.Model):
    """
    Append-only audit log of significant events related to entries.

    IMMUTABLE: records must never be updated or deleted. The save() and
    delete() methods raise PermissionError on any attempt to mutate an
    existing record. Only AuditLog.objects.create() should ever be called.
    """

    ACTION_CREATED = "created"
    ACTION_UPDATED = "updated"
    ACTION_SUBMITTED = "submitted"
    ACTION_APPROVED = "approved"
    ACTION_RETURNED = "returned"
    ACTION_ARCHIVED = "archived"
    ACTION_IP_CLAIMED = "ip_claimed"
    ACTION_EXPORTED = "exported"
    ACTION_COMMENTED = "commented"

    ACTION_CHOICES = [
        (ACTION_CREATED, "Created"),
        (ACTION_UPDATED, "Updated"),
        (ACTION_SUBMITTED, "Submitted"),
        (ACTION_APPROVED, "Approved"),
        (ACTION_RETURNED, "Returned"),
        (ACTION_ARCHIVED, "Archived"),
        (ACTION_IP_CLAIMED, "IP Claimed"),
        (ACTION_EXPORTED, "Exported"),
        (ACTION_COMMENTED, "Commented"),
    ]

    entry = models.ForeignKey(
        Entry,
        on_delete=models.PROTECT,
        related_name="audit_logs",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "entries_auditlog"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            raise PermissionError("AuditLog records are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        raise PermissionError("AuditLog records cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.entry} — {self.action}"


class CommentThread(models.Model):
    """
    Thread of comments associated with an entry and optional text range.
    """

    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="comment_threads",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_threads",
    )
    # Stores serialized rich-text anchor data; TextField to avoid truncation.
    anchor_start = models.TextField(blank=True)
    anchor_end = models.TextField(blank=True)

    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "entries_commentthread"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Thread on entry {self.entry_id} by {self.created_by_id}"


class Comment(models.Model):
    """
    Individual comment within a thread.
    """

    thread = models.ForeignKey(
        CommentThread,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "entries_comment"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment {self.pk} by {self.author_id}"


class IPClaim(models.Model):
    """
    IP claim associated with an entry.
    """

    entry = models.OneToOneField(
        Entry,
        on_delete=models.CASCADE,
        related_name="ip_claim",
    )
    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ip_claims",
    )
    novelty_description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "entries_ipclaim"

    def __str__(self) -> str:
        return f"IP claim on entry {self.entry_id} by {self.claimant_id}"


class EntrySection(models.Model):
    """
    Content authored for a single TemplateSection within a templated Entry.

    content may be blank during editing; emptiness is only enforced at submit
    time via submit_entry() in services.py.
    """

    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="sections",
    )
    template_section = models.ForeignKey(
        TemplateSection,
        on_delete=models.CASCADE,
        related_name="entry_sections",
    )
    content = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "entries_entrysection"
        unique_together = ("entry", "template_section")

    def __str__(self) -> str:
        return f"Section '{self.template_section.title}' for entry {self.entry_id}"
