# ==============================================================================
# Online Labnotebook — Makefile
# ==============================================================================
# Usage:
#   make <target>
#
# All docker targets require the stack to be running: make up
# ==============================================================================

COMPOSE        := docker compose -f docker-compose.yml
API_SERVICE    := logbook-api
DJANGO_EXEC    := $(COMPOSE) exec $(API_SERVICE) python manage.py
PYTEST_EXEC    := $(COMPOSE) exec $(API_SERVICE) python -m pytest

# Default: show help
.DEFAULT_GOAL := help

.PHONY: help up down restart logs \
        migrate makemigrations showmigrations shell \
        test test-users test-projects test-entries test-templates test-verbose test-failed \
        lint lint-fix

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------

help:
	@echo ""
	@echo "  Online Labnotebook — available targets"
	@echo ""
	@echo "  Stack"
	@echo "    make up               Start all services"
	@echo "    make down             Stop all services"
	@echo "    make restart          Restart all services"
	@echo "    make logs             Follow logs for all services"
	@echo ""
	@echo "  Database"
	@echo "    make migrate          Apply all pending migrations"
	@echo "    make makemigrations   Generate new migrations"
	@echo "    make showmigrations   Show migration state"
	@echo "    make shell            Open Django shell"
	@echo ""
	@echo "  Testing"
	@echo "    make test             Run all model tests"
	@echo "    make test-users       Run users model tests only"
	@echo "    make test-projects    Run projects model tests only"
	@echo "    make test-entries     Run entries model tests only"
	@echo "    make test-templates   Run templates_engine model tests only"
	@echo "    make test-verbose     Run all tests with full output"
	@echo "    make test-failed      Re-run only previously failed tests"
	@echo ""


# ------------------------------------------------------------------------------
# Stack
# ------------------------------------------------------------------------------

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

# ------------------------------------------------------------------------------
# Database
# ------------------------------------------------------------------------------

migrate:
	$(DJANGO_EXEC) migrate

makemigrations:
	$(DJANGO_EXEC) makemigrations

showmigrations:
	$(DJANGO_EXEC) showmigrations

shell:
	$(DJANGO_EXEC) shell

# ------------------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------------------

test:
	$(PYTEST_EXEC) apps/users/tests/ apps/projects/tests/ apps/entries/tests/ apps/templates_engine/tests/

test-users:
	$(PYTEST_EXEC) apps/users/tests/ -v

test-projects:
	$(PYTEST_EXEC) apps/projects/tests/ -v

test-entries:
	$(PYTEST_EXEC) apps/entries/tests/ -v

test-templates:
	$(PYTEST_EXEC) apps/templates_engine/tests/ -v

test-verbose:
	$(PYTEST_EXEC) apps/users/tests/ apps/projects/tests/ apps/entries/tests/ apps/templates_engine/tests/ -v

test-failed:
	$(PYTEST_EXEC) apps/users/tests/ apps/projects/tests/ apps/entries/tests/ apps/templates_engine/tests/ --lf -v


