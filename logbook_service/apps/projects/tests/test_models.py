"""
Tests for apps.projects.models — Project, Experiment, ProjectMembership.

Coverage:
  TC-PRJ-001  Project creation with required fields
  TC-PRJ-002  Project __str__
  TC-PRJ-003  Project defaults (is_archived=False)
  TC-PRJ-004  Project description is optional
  TC-PRJ-005  Project cascade-deletes when owner is deleted
  TC-PRJ-006  Experiment creation
  TC-PRJ-007  Experiment __str__
  TC-PRJ-008  Experiment defaults (is_archived=False, nullable dates)
  TC-PRJ-009  Experiment FK cascade-deletes when project is deleted
  TC-PRJ-010  ProjectMembership creation
  TC-PRJ-011  ProjectMembership __str__
  TC-PRJ-012  ProjectMembership default role is 'viewer'
  TC-PRJ-013  ProjectMembership unique_together (user, project)
  TC-PRJ-014  ProjectMembership role choices are valid constants
  TC-PRJ-015  Multiple memberships on different projects for same user
  TC-PRJ-016  Project Meta ordering
"""

import pytest
from django.db import IntegrityError

from apps.projects.models import Experiment, Project, ProjectMembership


@pytest.mark.django_db
class TestProject:
    def test_create_project(self, user):
        """TC-PRJ-001: Project is created with required fields and gets a PK."""
        p = Project.objects.create(owner=user, name="My Project")
        assert p.pk is not None
        assert p.name == "My Project"
        assert p.owner == user

    def test_str(self, project):
        """TC-PRJ-002: __str__ returns project name."""
        assert str(project) == project.name

    def test_default_is_archived_false(self, project):
        """TC-PRJ-003: is_archived defaults to False."""
        assert project.is_archived is False

    def test_description_optional(self, user, db):
        """TC-PRJ-004: description can be blank."""
        p = Project.objects.create(owner=user, name="No Desc", description="")
        assert p.description == ""

    def test_cascade_delete_on_owner_delete(self, user, db):
        """TC-PRJ-005: Deleting the owner cascades to owned projects."""
        p = Project.objects.create(owner=user, name="Soon Gone")
        pid = p.pk
        user.delete()
        assert not Project.objects.filter(pk=pid).exists()

    def test_meta_ordering(self):
        """TC-PRJ-016: Projects are ordered alphabetically by name."""
        assert Project._meta.ordering == ["name"]

    def test_meta_db_table(self):
        assert Project._meta.db_table == "projects_project"


@pytest.mark.django_db
class TestExperiment:
    def test_create_experiment(self, project):
        """TC-PRJ-006: Experiment is created linked to a project."""
        e = Experiment.objects.create(project=project, name="Exp A")
        assert e.pk is not None
        assert e.project == project

    def test_str(self, experiment):
        """TC-PRJ-007: __str__ returns experiment name."""
        assert str(experiment) == experiment.name

    def test_defaults(self, experiment):
        """TC-PRJ-008: is_archived defaults to False; dates are nullable."""
        assert experiment.is_archived is False
        assert experiment.start_date is None
        assert experiment.end_date is None

    def test_dates_stored(self, project, db):
        """TC-PRJ-008b: start_date and end_date are persisted when provided."""
        from datetime import date

        e = Experiment.objects.create(
            project=project,
            name="Dated",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
        )
        e.refresh_from_db()
        assert e.start_date == date(2026, 1, 1)
        assert e.end_date == date(2026, 6, 30)

    def test_cascade_delete_on_project_delete(self, project, db):
        """TC-PRJ-009: Deleting project cascades to its experiments."""
        e = Experiment.objects.create(project=project, name="Will Be Gone")
        eid = e.pk
        project.delete()
        assert not Experiment.objects.filter(pk=eid).exists()

    def test_description_optional(self, project, db):
        """Experiment description may be blank."""
        e = Experiment.objects.create(project=project, name="No Desc", description="")
        assert e.description == ""


@pytest.mark.django_db
class TestProjectMembership:
    def test_create_membership(self, user, project):
        """TC-PRJ-010: Membership record is created with a PK."""
        m = ProjectMembership.objects.create(
            user=user, project=project, role=ProjectMembership.ROLE_EDITOR
        )
        assert m.pk is not None

    def test_str(self, user, project):
        """TC-PRJ-011: __str__ shows user, project, and role."""
        m = ProjectMembership.objects.create(
            user=user, project=project, role=ProjectMembership.ROLE_ADMIN
        )
        expected = f"{user} in {project} ({ProjectMembership.ROLE_ADMIN})"
        assert str(m) == expected

    def test_default_role_is_viewer(self, user, project):
        """TC-PRJ-012: Default role is 'viewer' when not specified."""
        m = ProjectMembership.objects.create(user=user, project=project)
        assert m.role == ProjectMembership.ROLE_VIEWER

    def test_unique_together_user_project(self, user, project):
        """TC-PRJ-013: A second membership for the same (user, project) raises IntegrityError."""
        ProjectMembership.objects.create(user=user, project=project)
        with pytest.raises(IntegrityError):
            ProjectMembership.objects.create(user=user, project=project)

    def test_same_user_different_projects(self, user, project, other_project):
        """TC-PRJ-015: Same user may belong to two distinct projects."""
        m1 = ProjectMembership.objects.create(user=user, project=project)
        m2 = ProjectMembership.objects.create(user=user, project=other_project)
        assert m1.pk != m2.pk

    def test_role_choices_constants(self):
        """TC-PRJ-014: Role constant values match expected strings."""
        assert ProjectMembership.ROLE_VIEWER == "viewer"
        assert ProjectMembership.ROLE_EDITOR == "editor"
        assert ProjectMembership.ROLE_ADMIN == "admin"

    def test_is_active_default_true(self, user, project):
        """is_active defaults to True."""
        m = ProjectMembership.objects.create(user=user, project=project)
        assert m.is_active is True

    def test_meta_db_table(self):
        assert ProjectMembership._meta.db_table == "projects_projectmembership"
