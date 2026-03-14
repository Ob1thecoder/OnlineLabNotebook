"""
Tests for apps.users.models — User and UserManager.

Coverage:
  TC-USR-001  create_user happy path
  TC-USR-002  create_user rejects blank email
  TC-USR-003  email is normalised on creation
  TC-USR-004  password is hashed (not stored in plaintext)
  TC-USR-005  email uniqueness constraint
  TC-USR-006  __str__ returns email
  TC-USR-007  default flag values
  TC-USR-008  full_name field is optional
  TC-USR-009  create_superuser sets is_staff and is_superuser
  TC-USR-010  USERNAME_FIELD is email (no username column)
  TC-USR-011  ordering is by -date_joined (Meta)
"""

import pytest
from django.db import IntegrityError

from apps.users.models import User


@pytest.mark.django_db
class TestUserManager:
    def test_create_user_happy_path(self, make_user):
        """TC-USR-001: create_user persists a user and returns the instance."""
        u = make_user(email="happy@example.com")
        assert u.pk is not None
        assert u.email == "happy@example.com"

    def test_create_user_empty_email_raises(self, db):
        """TC-USR-002: create_user raises ValueError when email is blank."""
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email="", password="pass")

    def test_email_normalised(self, db):
        """TC-USR-003: Domain part of email is lowercased during creation."""
        u = User.objects.create_user(email="Test@EXAMPLE.COM", password="pass")
        assert u.email == "Test@example.com"

    def test_password_is_hashed(self, make_user):
        """TC-USR-004: The stored password is never the raw plaintext value."""
        u = make_user(email="hash@example.com", password="plaintext")
        assert u.password != "plaintext"
        assert u.check_password("plaintext") is True

    def test_create_superuser_sets_flags(self, db):
        """TC-USR-009: create_superuser grants is_staff and is_superuser."""
        su = User.objects.create_superuser(email="admin@example.com", password="pass")
        assert su.is_staff is True
        assert su.is_superuser is True


@pytest.mark.django_db
class TestUserModel:
    def test_str_returns_email(self, user):
        """TC-USR-006: __str__ is the user's email address."""
        assert str(user) == user.email

    def test_default_flags(self, make_user):
        """TC-USR-007: is_instructor and is_professional default to False."""
        u = make_user()
        assert u.is_instructor is False
        assert u.is_professional is False

    def test_full_name_optional(self, db):
        """TC-USR-008: full_name can be blank."""
        u = User.objects.create_user(email="noname@example.com", password="pass", full_name="")
        assert u.full_name == ""

    def test_full_name_stored(self, db):
        """TC-USR-008b: full_name is persisted correctly when provided."""
        u = User.objects.create_user(
            email="named@example.com", password="pass", full_name="Alice Smith"
        )
        u.refresh_from_db()
        assert u.full_name == "Alice Smith"

    def test_email_uniqueness(self, make_user):
        """TC-USR-005: Two users with the same email raise IntegrityError."""
        make_user(email="dup@example.com")
        with pytest.raises(IntegrityError):
            User.objects.create_user(email="dup@example.com", password="pass")

    def test_no_username_field(self):
        """TC-USR-010: username attribute does not exist on the model."""
        assert not hasattr(User, "username") or User.username is None

    def test_username_field_is_email(self):
        """TC-USR-010b: USERNAME_FIELD is set to 'email'."""
        assert User.USERNAME_FIELD == "email"

    def test_required_fields_empty(self):
        """TC-USR-010c: REQUIRED_FIELDS is empty (email-only auth)."""
        assert User.REQUIRED_FIELDS == []

    def test_meta_ordering(self):
        """TC-USR-011: Meta ordering is by descending date_joined."""
        assert User._meta.ordering == ["-date_joined"]

    def test_meta_db_table(self):
        """TC-USR-011b: Table name is 'users_user'."""
        assert User._meta.db_table == "users_user"
