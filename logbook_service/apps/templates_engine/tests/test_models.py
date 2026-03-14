"""
Tests for apps.templates_engine.models — EntryTemplate, TemplateSection.

Coverage:
  EntryTemplate:
    TC-TPL-001  creation with required fields
    TC-TPL-002  __str__
    TC-TPL-003  slug uniqueness
    TC-TPL-004  default discipline is 'general'
    TC-TPL-005  is_builtin defaults to False; is_active defaults to True
    TC-TPL-006  created_by is nullable (built-in templates have no owner)
    TC-TPL-007  created_by SET_NULL when user is deleted
    TC-TPL-008  discipline choices constants
    TC-TPL-009  Meta ordering is by name

  TemplateSection:
    TC-SEC-001  creation
    TC-SEC-002  __str__
    TC-SEC-003  unique_together (template, order)
    TC-SEC-004  same order on different templates is allowed
    TC-SEC-005  is_required defaults to True
    TC-SEC-006  order defaults to 0
    TC-SEC-007  cascade-delete when template is deleted
    TC-SEC-008  prompt may be blank
"""

import pytest
from django.db import IntegrityError

from apps.templates_engine.models import EntryTemplate, TemplateSection


# ---------------------------------------------------------------------------
# EntryTemplate
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntryTemplate:
    def test_create_minimal(self, db):
        """TC-TPL-001: EntryTemplate is created with only name and slug."""
        t = EntryTemplate.objects.create(name="Basic", slug="basic")
        assert t.pk is not None

    def test_str(self, entry_template):
        """TC-TPL-002: __str__ returns the template name."""
        assert str(entry_template) == entry_template.name

    def test_slug_uniqueness(self, entry_template, db):
        """TC-TPL-003: Two templates with the same slug raise IntegrityError."""
        with pytest.raises(IntegrityError):
            EntryTemplate.objects.create(name="Duplicate", slug=entry_template.slug)

    def test_default_discipline_is_general(self, db):
        """TC-TPL-004: discipline defaults to 'general' when not specified."""
        t = EntryTemplate.objects.create(name="Def Disc", slug="def-disc")
        assert t.discipline == EntryTemplate.DISCIPLINE_GENERAL

    def test_default_is_builtin_false(self, db):
        """TC-TPL-005a: is_builtin defaults to False."""
        t = EntryTemplate.objects.create(name="Custom", slug="custom-tpl")
        assert t.is_builtin is False

    def test_default_is_active_true(self, db):
        """TC-TPL-005b: is_active defaults to True."""
        t = EntryTemplate.objects.create(name="Active", slug="active-tpl")
        assert t.is_active is True

    def test_created_by_nullable_for_builtin(self, db):
        """TC-TPL-006: created_by may be None for built-in templates."""
        t = EntryTemplate.objects.create(
            name="Built-in", slug="builtin-tpl", is_builtin=True, created_by=None
        )
        assert t.created_by is None

    def test_created_by_set_null_on_user_delete(self, make_user, db):
        """TC-TPL-007: created_by becomes None when the creator user is deleted."""
        instructor = make_user(email="instructor@example.com")
        t = EntryTemplate.objects.create(
            name="Instructor TPL", slug="instructor-tpl", created_by=instructor
        )
        instructor.delete()
        t.refresh_from_db()
        assert t.created_by is None

    def test_discipline_choices_constants(self):
        """TC-TPL-008: All DISCIPLINE_ constants have expected string values."""
        assert EntryTemplate.DISCIPLINE_GENERAL == "general"
        assert EntryTemplate.DISCIPLINE_ELECTRICAL == "electrical"
        assert EntryTemplate.DISCIPLINE_MATERIALS == "materials"
        assert EntryTemplate.DISCIPLINE_FLUIDS == "fluids"
        assert EntryTemplate.DISCIPLINE_STRUCTURAL == "structural"
        assert EntryTemplate.DISCIPLINE_SOFTWARE == "software"
        assert EntryTemplate.DISCIPLINE_FIELD_OBS == "field_observation"

    def test_all_disciplines_are_in_choices(self):
        """Every DISCIPLINE_ constant must appear as a choice key."""
        choice_keys = {key for key, _ in EntryTemplate.DISCIPLINE_CHOICES}
        constants = {
            EntryTemplate.DISCIPLINE_GENERAL,
            EntryTemplate.DISCIPLINE_ELECTRICAL,
            EntryTemplate.DISCIPLINE_MATERIALS,
            EntryTemplate.DISCIPLINE_FLUIDS,
            EntryTemplate.DISCIPLINE_STRUCTURAL,
            EntryTemplate.DISCIPLINE_SOFTWARE,
            EntryTemplate.DISCIPLINE_FIELD_OBS,
        }
        assert constants == choice_keys

    def test_meta_ordering(self):
        """TC-TPL-009: EntryTemplate is ordered alphabetically by name."""
        assert EntryTemplate._meta.ordering == ["name"]

    def test_meta_db_table(self):
        assert EntryTemplate._meta.db_table == "templates_entrytemplate"


# ---------------------------------------------------------------------------
# TemplateSection
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTemplateSection:
    def test_create_section(self, entry_template):
        """TC-SEC-001: TemplateSection is created and linked to its template."""
        sec = TemplateSection.objects.create(
            template=entry_template, title="Objective", order=1
        )
        assert sec.pk is not None
        assert sec.template == entry_template

    def test_str(self, entry_template, db):
        """TC-SEC-002: __str__ returns the section title."""
        sec = TemplateSection.objects.create(
            template=entry_template, title="Hypothesis", order=1
        )
        assert str(sec) == "Hypothesis"

    def test_unique_together_template_order(self, entry_template, db):
        """TC-SEC-003: Two sections with the same (template, order) raise IntegrityError."""
        TemplateSection.objects.create(
            template=entry_template, title="First", order=1
        )
        with pytest.raises(IntegrityError):
            TemplateSection.objects.create(
                template=entry_template, title="Duplicate Order", order=1
            )

    def test_same_order_different_templates(self, db):
        """TC-SEC-004: order=1 may exist on two different templates without conflict."""
        t1 = EntryTemplate.objects.create(name="T1", slug="t1")
        t2 = EntryTemplate.objects.create(name="T2", slug="t2")
        s1 = TemplateSection.objects.create(template=t1, title="S1", order=1)
        s2 = TemplateSection.objects.create(template=t2, title="S2", order=1)
        assert s1.pk != s2.pk

    def test_is_required_default_true(self, entry_template, db):
        """TC-SEC-005: is_required defaults to True."""
        sec = TemplateSection.objects.create(
            template=entry_template, title="Required", order=1
        )
        assert sec.is_required is True

    def test_order_default_is_zero(self, entry_template, db):
        """TC-SEC-006: order defaults to 0 when not provided."""
        sec = TemplateSection.objects.create(
            template=entry_template, title="First Ever"
        )
        assert sec.order == 0

    def test_cascade_delete_with_template(self, db):
        """TC-SEC-007: TemplateSection is deleted when its parent template is deleted."""
        t = EntryTemplate.objects.create(name="Temp", slug="temp-del")
        sec = TemplateSection.objects.create(template=t, title="Section", order=1)
        sid = sec.pk
        t.delete()
        assert not TemplateSection.objects.filter(pk=sid).exists()

    def test_prompt_optional(self, entry_template, db):
        """TC-SEC-008: prompt may be blank."""
        sec = TemplateSection.objects.create(
            template=entry_template, title="No Prompt", order=1, prompt=""
        )
        assert sec.prompt == ""

    def test_meta_db_table(self):
        assert TemplateSection._meta.db_table == "templates_templatesection"
