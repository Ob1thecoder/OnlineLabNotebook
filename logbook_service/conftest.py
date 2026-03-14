"""
Root conftest — shared fixtures for all model tests.
"""
import pytest

from apps.entries.models import AuditLog, Comment, CommentThread, Entry, EntryVersion, IPClaim
from apps.projects.models import Experiment, Project, ProjectMembership
from apps.templates_engine.models import EntryTemplate, TemplateSection
from apps.users.models import User


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@pytest.fixture
def make_user(db):
    """Factory: create a unique User on each call."""
    _counter = {"n": 0}

    def _make(email=None, password="password123", **kwargs):
        _counter["n"] += 1
        email = email or f"user{_counter['n']}@example.com"
        return User.objects.create_user(email=email, password=password, **kwargs)

    return _make


@pytest.fixture
def user(make_user):
    return make_user(email="alice@example.com")


@pytest.fixture
def other_user(make_user):
    return make_user(email="bob@example.com")


# ---------------------------------------------------------------------------
# Projects / Experiments
# ---------------------------------------------------------------------------

@pytest.fixture
def project(db, user):
    return Project.objects.create(owner=user, name="Test Project")


@pytest.fixture
def other_project(db, user):
    return Project.objects.create(owner=user, name="Other Project")


@pytest.fixture
def experiment(db, project):
    return Experiment.objects.create(project=project, name="Test Experiment")


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

@pytest.fixture
def entry_template(db):
    return EntryTemplate.objects.create(
        name="General Template",
        slug="general-template",
        discipline=EntryTemplate.DISCIPLINE_GENERAL,
        is_builtin=True,
    )


# ---------------------------------------------------------------------------
# Entries
# ---------------------------------------------------------------------------

@pytest.fixture
def entry(db, project, user):
    return Entry.objects.create(project=project, author=user, title="Sample Entry")


@pytest.fixture
def entry_with_experiment(db, project, experiment, user):
    return Entry.objects.create(
        project=project,
        experiment=experiment,
        author=user,
        title="Entry With Experiment",
    )
