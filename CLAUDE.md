# CLAUDE.md — Claude Code Configuration for Online Labnotebook

## Project Context

**App:** Online Labnotebook
**Stack:** Django 5 + Python 3.12 · Django REST Framework · Django Channels · Celery · PostgreSQL 16 · React 18 + TypeScript + Vite · Tailwind CSS
**Stage:** MVP Development — Phase 8A (Enhanced Dashboard Foundation)
**User Level:** Intermediate (comfortable with Django and React; newer to Channels and Celery)

## Directives

1. **Master Plan:** Always read `AGENTS.md` first. It contains the current phase and active tasks.
2. **Documentation:** Refer to `agent_docs/` for tech stack details, code patterns, and testing guides.
3. **Plan-First:** Propose a brief plan and wait for approval before writing any code.
4. **Incremental Build:** Build one small feature at a time. Test after each change before moving on.
5. **Pre-Commit:** Run pre-commit hooks before every commit; fix all failures before proceeding.
6. **No Linting:** Do not act as a linter. Run `npm run lint` or `ruff check .` if style checks are needed.
7. **Communication:** Be concise. Ask clarifying questions when requirements are ambiguous.
8. **Stay in Scope:** Do not add features outside the current phase. Document deferred ideas in the PRD.
9. **No Destructive Actions:** Never delete files, drop tables, or stop services without explicit confirmation.
10. **No Hardcoding:** Use constants, environment variables, or design tokens — never raw values in code.

## Commands

### Backend (Django)
- `docker compose up` — Start all services (API, worker, beat, Postgres, Redis, Nginx)
- `python manage.py runserver` — Start Django dev server (inside container or venv)
- `python manage.py makemigrations` — Generate migrations after model changes
- `python manage.py migrate` — Apply migrations
- `pytest` — Run all tests
- `ruff check .` — Check Python code style
- `celery -A config worker -l info` — Start Celery worker manually

### Frontend (React)
- `npm run dev` — Start Vite dev server (port 3000)
- `npm test` — Run frontend tests
- `npm run lint` — Check TypeScript / ESLint style
- `npm run build` — Production build

### Local URLs
- Django API: `http://localhost:8000/api/`
- React frontend: `http://localhost:3000`
- Django admin: `http://localhost:8000/admin/`
- Celery monitor (Flower): `http://localhost:5555`