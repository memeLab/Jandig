# CLAUDE.md – Jandig Codebase Guide

This file provides context for AI assistants working on the Jandig codebase.

---

## Project Overview

**Jandig** is a Django-based Progressive Web App (PWA) for creating and sharing augmented reality (AR) artwork. Users upload AR markers and 3D/video objects, compose them into *Artworks*, and group artworks into *Exhibits*. AR rendering is done client-side with AR.js.

- **Version**: 2.0.9
- **Python**: 3.13+
- **Package manager**: [UV](https://github.com/astral-sh/uv)

---

## Repository Layout

```
Jandig/
├── src/                    # All Django source code
│   ├── config/             # Django settings, URL routing, auth backends
│   ├── core/               # Main app: Markers, Objects, Artworks, Exhibits, Sounds
│   ├── users/              # User Profiles and authentication views
│   ├── blog/               # Blog/Memories feature (Posts, Categories, Clippings)
│   └── ui_tests/           # Playwright end-to-end tests
├── docs/                   # Sphinx documentation source + architecture docs
├── collection/             # Sample media files used in tests (markers, objects, sounds)
├── locale/                 # i18n translation files (en, pt_BR, es_ES)
├── etc/                    # Traefik and Mailpit configuration
├── .github/                # CI/CD workflows, CONTRIBUTING.md, ROADMAP.md
├── docker-compose.yml      # Docker orchestration (Django, PostgreSQL, MinIO, Mailpit, Traefik)
├── Dockerfile              # Multi-stage build (base + local_dev targets)
├── pyproject.toml          # Dependencies and tool configuration (UV, ruff, pytest, djlint)
├── Makefile                # Developer shortcuts
└── run.sh                  # Container entrypoint
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | Django 6.0+ |
| REST API | Django REST Framework 3.15+, drf-nested-routers |
| Authentication | JWT via djangorestframework-simplejwt |
| ASGI server | Granian 2.5+ |
| Database | PostgreSQL 16 (psycopg3) |
| Object storage | MinIO (dev) / AWS S3 (prod), via django-storages + boto3 |
| Templates | Jinja2 3.1+ (configured in `config/jinja2.py`) |
| Dynamic UI | HTMX (django-htmx) |
| Audit logging | django-pghistory |
| AR rendering | AR.js (client-side, vanilla JS) |
| Email testing | Mailpit |
| Reverse proxy | Traefik v3.3+ |
| Error tracking | Sentry SDK (optional, set via `SENTRY_DSN`) |

---

## Development Setup

### Recommended: Docker Compose

```bash
docker compose up --watch    # Start all services with live reload
```

Services:
- `django` – app on port 8000
- `postgres` – PostgreSQL 16
- `minio` – S3-compatible storage (console on port 9001)
- `mailpit` – email UI on port 8025
- `traefik` – reverse proxy on port 80

### Alternative: UV + Django dev server

```bash
# Copy env file and configure
cp .envs/.example .env
# Edit .env as needed

DJANGO_READ_DOT_ENV_FILE=True uv run python src/manage.py runserver
```

> AR features require HTTPS. Use [ngrok](https://ngrok.com/) for mobile testing:
> ```bash
> ngrok http 8000
> ```

---

## Common Commands (Makefile)

| Command | Description |
|---|---|
| `make test` | Run unit tests (pytest, parallel with `-n4`) |
| `make test-ui` | Run Playwright E2E tests |
| `make test-all` | Run all tests including UI |
| `make lint` | Format code: djlint + ruff format + ruff check --fix |
| `make check` | Ruff static analysis only (no changes) |
| `make migrations` | `makemigrations` (no Docker required) |
| `make migrate` | Apply migrations inside running container |
| `make collectstatic` | Collect static files in container |
| `make translate_pt` | Extract + merge Portuguese-BR translations |
| `make translate_es` | Extract + merge Spanish translations |
| `make gen` | Generate Playwright test code via codegen |

---

## Django Application Structure

### `src/core/` – Core Domain

**Models** (`core/models.py`):
- `Sound` – Audio files (owner, title, author, source file)
- `Marker` – AR marker image; `.patt` file auto-generated on save
- `Object` – 3D/video/GIF media (GLB, MP4, WEBM, GIF)
- `Artwork` – Composition of a Marker + Object + optional Sound
- `Exhibit` – Named collection of Artworks (type: AR or MR)

All models:
- Extend `TimeStampedModel` (from django-extensions) → `created` / `modified` fields
- Are decorated with `@pghistory.track()` for audit history
- Cache file sizes to avoid repeated S3 HEAD requests

**Viewsets** (`core/views/viewsets.py`): DRF ViewSets using `ListModelMixin` + `RetrieveModelMixin`.

**API views** (`core/views/api_views.py`): Custom views including `MarkerGeneratorAPIView`.

**Templates**: Jinja2 files under `core/jinja2/` (not `core/templates/`).

### `src/users/` – User & Profile

- `Profile` – OneToOne extension of Django's `User`; tracks counts of created content
- Auto-created via Django signal when a `User` is created
- Supports email **or** username login (custom auth backend in `config/auth_backends.py`)

### `src/blog/` – Memories / Blog

- `Post`, `Category`, `PostImage`, `Clipping`
- Supports draft/published status workflow

### `src/config/` – Project Configuration

| File | Purpose |
|---|---|
| `settings.py` | Main Django settings (reads `.env` via django-environ) |
| `test_settings.py` | Overrides for tests: SQLite in-memory, InMemoryStorage |
| `urls.py` | Root URL configuration |
| `jinja2.py` | Jinja2 environment setup |
| `storage_backends.py` | `PublicMediaStorage` and `StaticStorage` for S3 |
| `auth_backends.py` | Email-or-username authentication backend |

---

## REST API

Base path: `/api/v1/`

| Endpoint | Methods | Description |
|---|---|---|
| `markers/` | GET, POST | List / create markers |
| `markers/<id>/` | GET | Retrieve marker |
| `objects/` | GET, POST | List / create objects |
| `artworks/` | GET, POST | List / create artworks |
| `exhibits/` | GET, POST | List / create exhibits |
| `sounds/` | GET, POST | List / create sounds |
| `profiles/` | GET | List profiles |
| `auth/login/` | POST | Obtain JWT token pair |
| `auth/refresh/` | POST | Refresh JWT access token |
| `auth/verify/` | POST | Verify JWT token |
| `markergenerator/` | POST | Generate AR marker `.patt` file |
| `status/` | GET | Health check |

**Pagination**: `LimitOffsetPagination`, default page size 20 (40 for modal views).

**JWT settings**: 5-minute access tokens, 1-day refresh tokens. Custom claims include `user_profile_id`, `user_id`, `username`.

---

## Testing

### Running Tests

```bash
# Unit tests (inside or outside container)
make test

# Or directly with pytest
docker compose exec django pytest src/core src/users src/blog

# E2E tests (requires running container)
make test-ui

# With coverage
docker compose exec django pytest --cov=src --cov-report=xml src/core src/users src/blog
```

### Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.test_settings"
testpaths = ["src/core", "src/users", "src/blog", "src/ui_tests"]
pythonpath = "src"
addopts = "-n4"   # parallel execution with 4 workers
```

### Test Conventions

- Test files: named `test_*.py`, `*_tests.py`, or `tests.py`
- Use `factory-boy` for fixtures (`ProfileFactory`, `ArtworkFactory`, etc.)
- Sample media for factories is randomly selected from `/collection/`
- `src/ui_tests/` contains Playwright tests; use `make gen` to record new interactions
- Coverage omits: migrations, `admin.py`, `asgi.py`, `wsgi.py`, `manage.py`

---

## Code Style & Conventions

### Python

- Linter/formatter: **ruff** (line length 88, target Python 3.13)
- PEP 8 compliant
- Run `make lint` before committing

### HTML / Jinja2

- Formatter: **djlint** with `profile = "jinja"`, extension `.jinja2`
- HTML element IDs: prefix with `id_` → e.g., `id="id_menu-bar"`
- CSS classes: plain name → e.g., `class="menu-bar"`

### JavaScript

- Vanilla JS (no build step)
- StandardJS style conventions

### Django Patterns

- Use DRF `ViewSet` + mixins rather than `APIView` where possible
- New models should extend `TimeStampedModel` and use `@pghistory.track()`
- Signal handlers live in `apps.py` (connected in `ready()`) or `signals.py`
- Use `ContentMixin` for views that render HTML fragments for HTMX

---

## Internationalization

Supported locales: `en`, `pt_BR`, `es_ES`.

Translation files are under `locale/<lang>/LC_MESSAGES/django.po`.

Workflow combines Django `makemessages` + Babel extraction for Jinja2 strings:

```bash
make translate_pt   # Portuguese-BR
make translate_es   # Spanish
```

---

## Environment Variables

Copy `.envs/.example` to `.env`. Key variables:

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (required) |
| `DJANGO_DEBUG` | Enable debug mode |
| `DATABASE_URL` | PostgreSQL connection string |
| `USE_GRANIAN` | Use Granian ASGI server (`true`/`false`) |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | S3/MinIO credentials |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name |
| `AWS_S3_ENDPOINT_URL` | MinIO endpoint (dev) |
| `SENTRY_DSN` | Sentry error tracking (optional) |
| `DJANGO_ADMIN_URL` | Custom admin URL path (security) |
| `DJANGO_READ_DOT_ENV_FILE` | Load `.env` file (`True` for local dev) |

---

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

| Workflow | Trigger | Actions |
|---|---|---|
| `Linter.yml` | Every push | ruff check + ruff format |
| `PipelineRC.yml` | `develop` branch / tags | pytest → coverage → SonarQube → Docker build → DockerHub push → AWS ECS deploy |
| `PipelineProduction.yml` | Production tags | Production deployment |

Docker images: `jandigarte/django:dev` and `jandigarte/django:<tag>`

---

## Branch & PR Conventions

From `.github/CONTRIBUTING.md`:

- Branch names: `feature/<issueID>-short-description`
- All work must be tracked by a GitHub issue
- Open PR immediately after first commit (as `[WIP]`)
- PR title format: `[WIP] <issue number> - <issue title>`; change to `[REVIEW]` when ready
- Target branch: `develop`

---

## Key Files Quick Reference

| File | Purpose |
|---|---|
| `src/config/settings.py` | All Django settings |
| `src/config/urls.py` | Root URL routing |
| `src/core/models.py` | Marker, Object, Artwork, Exhibit, Sound models |
| `src/users/models.py` | Profile model |
| `src/core/views/viewsets.py` | DRF ViewSets |
| `src/core/views/api_views.py` | Custom API views |
| `pyproject.toml` | Dependencies + ruff/pytest/djlint config |
| `Makefile` | All developer shortcuts |
| `docker-compose.yml` | Local service orchestration |
| `.envs/.example` | Environment variable template |
| `docs/architecture-document.md` | Software Architecture Document |
