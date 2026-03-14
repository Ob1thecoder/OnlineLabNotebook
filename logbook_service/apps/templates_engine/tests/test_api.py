import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.templates_engine.models import EntryTemplate, TemplateSection


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def inactive_template(db):
    return EntryTemplate.objects.create(
        name="Inactive Template",
        slug="inactive-template",
        discipline=EntryTemplate.DISCIPLINE_GENERAL,
        is_active=False,
    )


@pytest.fixture
def electrical_template(db):
    t = EntryTemplate.objects.create(
        name="Circuit Testing",
        slug="circuit-testing-test",
        description="Template for circuit tests.",
        discipline=EntryTemplate.DISCIPLINE_ELECTRICAL,
        is_builtin=True,
    )
    TemplateSection.objects.create(template=t, title="Objective", order=0)
    TemplateSection.objects.create(template=t, title="Results", order=1)
    return t


@pytest.mark.django_db
class TestTemplateListAPI:
    def test_authenticated_list_returns_200(self, auth_client, entry_template):
        """TC-TAPI-001: Authenticated GET /api/templates/ returns 200."""
        resp = auth_client.get("/api/templates/")
        assert resp.status_code == 200

    def test_unauthenticated_returns_401(self, db, entry_template):
        """TC-TAPI-002: Unauthenticated request returns 401."""
        resp = APIClient().get("/api/templates/")
        assert resp.status_code == 401

    def test_only_active_templates_returned(self, auth_client, entry_template, inactive_template):
        """TC-TAPI-003: Inactive templates are excluded from list."""
        resp = auth_client.get("/api/templates/")
        slugs = [t["slug"] for t in resp.data["results"]]
        assert entry_template.slug in slugs
        assert inactive_template.slug not in slugs

    def test_discipline_filter_exact_match(self, auth_client, entry_template, electrical_template):
        """TC-TAPI-004: ?discipline=electrical returns only matching templates."""
        resp = auth_client.get("/api/templates/?discipline=electrical")
        slugs = [t["slug"] for t in resp.data["results"]]
        assert electrical_template.slug in slugs
        assert entry_template.slug not in slugs

    def test_discipline_filter_no_match_returns_empty(self, auth_client, entry_template):
        """TC-TAPI-005: ?discipline with no match returns empty list, not 400."""
        resp = auth_client.get("/api/templates/?discipline=nonexistent")
        assert resp.status_code == 200
        assert resp.data["results"] == []

    def test_search_matches_name_case_insensitive(self, auth_client, electrical_template):
        """TC-TAPI-006: ?search matches template name case-insensitively."""
        resp = auth_client.get("/api/templates/?search=CIRCUIT")
        slugs = [t["slug"] for t in resp.data["results"]]
        assert electrical_template.slug in slugs

    def test_search_matches_description(self, auth_client, electrical_template):
        """TC-TAPI-007: ?search matches description case-insensitively."""
        resp = auth_client.get("/api/templates/?search=circuit tests")
        slugs = [t["slug"] for t in resp.data["results"]]
        assert electrical_template.slug in slugs

    def test_list_response_excludes_sections(self, auth_client, entry_template, template_section):
        """TC-TAPI-008: List response does not include a sections key."""
        resp = auth_client.get("/api/templates/")
        results = resp.data["results"]
        assert len(results) > 0
        assert "sections" not in results[0]

    def test_combined_filters_use_and_logic(self, auth_client, entry_template, electrical_template):
        """TC-TAPI-009: ?discipline= and ?search= are combined with AND."""
        resp = auth_client.get("/api/templates/?discipline=electrical&search=circuit")
        slugs = [t["slug"] for t in resp.data["results"]]
        assert electrical_template.slug in slugs
        assert entry_template.slug not in slugs


@pytest.mark.django_db
class TestTemplateDetailAPI:
    def test_detail_returns_200(self, auth_client, entry_template):
        """TC-TDET-001: GET /api/templates/{slug}/ returns 200."""
        resp = auth_client.get(f"/api/templates/{entry_template.slug}/")
        assert resp.status_code == 200

    def test_unknown_slug_returns_404(self, auth_client):
        """TC-TDET-002: Unknown slug returns 404."""
        resp = auth_client.get("/api/templates/does-not-exist/")
        assert resp.status_code == 404

    def test_detail_includes_sections_ordered(self, auth_client, electrical_template):
        """TC-TDET-003: Detail response includes nested sections ordered by order."""
        resp = auth_client.get(f"/api/templates/{electrical_template.slug}/")
        assert "sections" in resp.data
        orders = [s["order"] for s in resp.data["sections"]]
        assert orders == sorted(orders)
        assert len(resp.data["sections"]) == 2

    def test_inactive_template_returns_404(self, auth_client, inactive_template):
        """TC-TDET-004: Inactive template is excluded from queryset → 404."""
        resp = auth_client.get(f"/api/templates/{inactive_template.slug}/")
        assert resp.status_code == 404
