import pytest
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.entries.models import Entry, EntrySection
from apps.entries.services import submit_entry
from apps.projects.models import ProjectMembership
from apps.templates_engine.models import TemplateSection


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def editor_membership(db, project, user):
    return ProjectMembership.objects.create(
        project=project,
        user=user,
        role=ProjectMembership.ROLE_EDITOR,
    )


@pytest.fixture
def viewer_user(make_user):
    return make_user(email="viewer@example.com")


@pytest.fixture
def viewer_membership(db, project, viewer_user):
    return ProjectMembership.objects.create(
        project=project,
        user=viewer_user,
        role=ProjectMembership.ROLE_VIEWER,
    )


@pytest.fixture
def optional_section(db, entry_template):
    return TemplateSection.objects.create(
        template=entry_template,
        title="Notes",
        prompt="Optional notes.",
        is_required=False,
        order=1,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestEntrySectionModel:
    def test_create_with_content(self, entry_with_template, template_section):
        """TC-ESM-001: EntrySection created with entry and template_section."""
        es = EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="To measure voltage.",
        )
        assert es.pk is not None
        assert es.content == "To measure voltage."

    def test_blank_content_allowed(self, entry_with_template, template_section):
        """TC-ESM-002: content may be blank on creation."""
        es = EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="",
        )
        assert es.content == ""

    def test_unique_together_raises(self, entry_with_template, template_section):
        """TC-ESM-003: unique_together (entry, template_section) raises IntegrityError on duplicate."""
        EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="First.",
        )
        with pytest.raises(IntegrityError):
            EntrySection.objects.create(
                entry=entry_with_template,
                template_section=template_section,
                content="Duplicate.",
            )

    def test_cascade_delete_on_entry(self, entry_with_template, template_section):
        """TC-ESM-004: Deleting the entry cascades to EntrySection."""
        es = EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="content",
        )
        entry_id = entry_with_template.pk
        entry_with_template.delete()
        assert not EntrySection.objects.filter(pk=es.pk).exists()

    def test_cascade_delete_on_template_section(self, entry_with_template, template_section):
        """TC-ESM-005: Deleting the TemplateSection cascades to EntrySection."""
        es = EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="content",
        )
        template_section.delete()
        assert not EntrySection.objects.filter(pk=es.pk).exists()

    def test_str_includes_title_and_entry_id(self, entry_with_template, template_section):
        """TC-ESM-006: __str__ includes section title and entry id."""
        es = EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="content",
        )
        assert template_section.title in str(es)
        assert str(entry_with_template.pk) in str(es)


# ---------------------------------------------------------------------------
# PATCH /api/entries/{id}/sections/{section_id}/ tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSectionUpdateAPI:
    def test_patch_creates_entry_section(self, auth_client, entry_with_template, template_section, editor_membership):
        """TC-SAPU-001: PATCH creates EntrySection when none exists (upsert insert)."""
        url = f"/api/entries/{entry_with_template.pk}/sections/{template_section.pk}/"
        resp = auth_client.patch(url, {"content": "My objective."}, format="json")
        assert resp.status_code == 200
        assert EntrySection.objects.filter(
            entry=entry_with_template,
            template_section=template_section,
        ).exists()

    def test_patch_updates_existing_entry_section(self, auth_client, entry_with_template, template_section, editor_membership):
        """TC-SAPU-002: PATCH updates existing EntrySection (upsert update)."""
        EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="Old content.",
        )
        url = f"/api/entries/{entry_with_template.pk}/sections/{template_section.pk}/"
        resp = auth_client.patch(url, {"content": "Updated content."}, format="json")
        assert resp.status_code == 200
        assert resp.data["content"] == "Updated content."
        assert EntrySection.objects.filter(entry=entry_with_template).count() == 1

    def test_patch_blank_content_accepted(self, auth_client, entry_with_template, template_section, editor_membership):
        """TC-SAPU-003: PATCH with blank content is accepted (blank valid at save time)."""
        url = f"/api/entries/{entry_with_template.pk}/sections/{template_section.pk}/"
        resp = auth_client.patch(url, {"content": ""}, format="json")
        assert resp.status_code == 200

    def test_patch_wrong_section_returns_404(self, auth_client, entry_with_template, editor_membership, db):
        """TC-SAPU-004: 404 when section_id does not belong to entry's template."""
        from apps.templates_engine.models import EntryTemplate
        other_template = EntryTemplate.objects.create(
            name="Other", slug="other-tmpl", discipline=EntryTemplate.DISCIPLINE_GENERAL
        )
        other_section = TemplateSection.objects.create(
            template=other_template, title="X", order=0
        )
        url = f"/api/entries/{entry_with_template.pk}/sections/{other_section.pk}/"
        resp = auth_client.patch(url, {"content": "x"}, format="json")
        assert resp.status_code == 404

    def test_viewer_role_returns_403(self, entry_with_template, template_section, viewer_user, viewer_membership):
        """TC-SAPU-005: Viewer role cannot update sections (403)."""
        client = APIClient()
        client.force_authenticate(user=viewer_user)
        url = f"/api/entries/{entry_with_template.pk}/sections/{template_section.pk}/"
        resp = client.patch(url, {"content": "x"}, format="json")
        assert resp.status_code == 403

    def test_editor_role_returns_200(self, auth_client, entry_with_template, template_section, editor_membership):
        """TC-SAPU-006: Editor role can update sections (200)."""
        url = f"/api/entries/{entry_with_template.pk}/sections/{template_section.pk}/"
        resp = auth_client.patch(url, {"content": "x"}, format="json")
        assert resp.status_code == 200

    def test_unauthenticated_returns_401(self, entry_with_template, template_section):
        """TC-SAPU-007: Unauthenticated request returns 401."""
        url = f"/api/entries/{entry_with_template.pk}/sections/{template_section.pk}/"
        resp = APIClient().patch(url, {"content": "x"}, format="json")
        assert resp.status_code == 401

    def test_response_body_shape(self, auth_client, entry_with_template, template_section, editor_membership):
        """TC-SAPU-008: Response body matches EntrySectionSerializer shape."""
        url = f"/api/entries/{entry_with_template.pk}/sections/{template_section.pk}/"
        resp = auth_client.patch(url, {"content": "abc"}, format="json")
        assert resp.status_code == 200
        for key in ("id", "template_section", "template_section_title", "content", "updated_at"):
            assert key in resp.data


# ---------------------------------------------------------------------------
# submit_entry() section enforcement tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSubmitEntryWithSections:
    def test_submit_with_all_required_sections_filled(self, entry_with_template, template_section, user):
        """TC-SUB-001: submit succeeds when all required sections have content."""
        EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="The objective.",
        )
        result = submit_entry(entry=entry_with_template, actor=user)
        assert result.status == Entry.STATUS_SUBMITTED

    def test_submit_missing_required_section_raises(self, entry_with_template, template_section, user):
        """TC-SUB-002: submit raises ValidationError listing missing section title."""
        with pytest.raises(ValidationError) as exc:
            submit_entry(entry=entry_with_template, actor=user)
        assert template_section.title in str(exc.value.detail)

    def test_submit_blank_required_section_raises(self, entry_with_template, template_section, user):
        """TC-SUB-003: Required section with blank content raises ValidationError."""
        EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="",
        )
        with pytest.raises(ValidationError) as exc:
            submit_entry(entry=entry_with_template, actor=user)
        assert template_section.title in str(exc.value.detail)

    def test_submit_empty_optional_section_succeeds(
        self, entry_with_template, template_section, optional_section, user
    ):
        """TC-SUB-004: Optional section empty — submit still succeeds."""
        EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="Objective content.",
        )
        # optional_section intentionally has no EntrySection
        result = submit_entry(entry=entry_with_template, actor=user)
        assert result.status == Entry.STATUS_SUBMITTED

    def test_submit_entry_without_template(self, entry, user):
        """TC-SUB-005: Entry without template submits normally (no section check)."""
        result = submit_entry(entry=entry, actor=user)
        assert result.status == Entry.STATUS_SUBMITTED

    def test_submit_no_sections_at_all_raises_with_all_titles(
        self, entry_with_template, template_section, optional_section, user
    ):
        """TC-SUB-006: No EntrySection records → raises listing all required titles."""
        with pytest.raises(ValidationError) as exc:
            submit_entry(entry=entry_with_template, actor=user)
        assert template_section.title in str(exc.value.detail)


# ---------------------------------------------------------------------------
# EntrySerializer sections field tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestEntrySerializerSections:
    def test_templated_entry_includes_sections(
        self, auth_client, entry_with_template, template_section, editor_membership
    ):
        """TC-ESR-001: GET /api/entries/{id}/ for templated entry includes sections list."""
        EntrySection.objects.create(
            entry=entry_with_template,
            template_section=template_section,
            content="Some content.",
        )
        resp = auth_client.get(f"/api/entries/{entry_with_template.pk}/")
        assert resp.status_code == 200
        assert "sections" in resp.data
        assert len(resp.data["sections"]) == 1

    def test_non_templated_entry_sections_empty(self, auth_client, entry, editor_membership):
        """TC-ESR-002: GET /api/entries/{id}/ for non-templated entry returns sections as []."""
        resp = auth_client.get(f"/api/entries/{entry.pk}/")
        assert resp.status_code == 200
        assert resp.data["sections"] == []
