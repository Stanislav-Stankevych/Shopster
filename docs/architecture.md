# Architecture Overview

This document summarises how the Shopster platform is assembled and how the major components interact.

## High-Level Components

| Component | Description | Key Technologies |
| --- | --- | --- |
| Frontend | Next.js 15 storefront rendering catalog, checkout and content pages. | Next.js (App Router), React 18, TypeScript, NextAuth, Zustand, Algolia InstantSearch |
| Backend | Django REST API, authentication, blog/CMS, SEO metadata, Algolia sync. | Django 5, Django REST Framework, SimpleJWT, django-filter, django-taggit, django-quill, Sentry |
| Data Stores | Transactional and cache layers. | PostgreSQL 16, Redis 7 |
| Infrastructure | Container orchestration for local/prod parity. | Docker Compose, Gunicorn, Whitenoise, go-task, GitHub Actions |

```
Browser ⇄ Next.js frontend ⇄ Django API ⇄ PostgreSQL
                        ↘ Redis cache
                        ↘ Algolia (search index)
```

## Backend Modules

- **core** – project settings, middleware (`AdminEnglishMiddleware`), URL routing, ASGI/WSGI entry points.
- **accounts** – user profiles, JWT auth (`/api/auth/…` endpoints), password reset, signals.
- **shop** – catalog domain (products, categories, images, carts, orders, reviews). Includes soft-delete mixins, Algolia sync (`shop/search.py`), DRF serializers, custom filters, unit tests.
- **content** – blog posts with Quill-based body, tags, publishing workflow.
- **management commands** – `load_demo_data`, `sync_algolia_products` for bootstrapping and reindexing.

Key middleware/services:
- `django-redis` as cache backend, configurable via `REDIS_URL`.
- Sentry SDK hook (errors, performance tracing) enabled through env vars.
- Swagger/OpenAPI via `drf-spectacular`.

## Frontend Modules

- **app/** (Next.js App Router) – route groups for auth, products, checkout, blog, admin stats.
- **components/** – reusable UI (filters, product cards, Algolia search, layout providers).
- **lib/** – API clients, auth helpers, SEO helpers (`seo.ts`), Zustand cart store, Algolia client wrapper.
- **types/** – TypeScript definitions mirroring backend serializers.
- **Dockerfile.prod** – multi-stage build (dependencies → builder → runtime).

The frontend uses `NEXT_PUBLIC_API_BASE_URL` for server components, and a fallback using `window.location` when not provided (for dev setups).

## Deployment Topology

- Production Compose (`deploy/docker-compose.yml`) starts four services:
  - `web` – Gunicorn + Django.
  - `frontend` – Next.js production server.
  - `db` – PostgreSQL.
  - `redis` – Redis cache.
- Static files are served via Whitenoise; media files live in a mounted volume (`media_volume`).
- Environment files live on the server under `/srv/vebsayt` (`.env`, `.env.local.frontend`).
- Docker Hub images (`stanyslav/vebsaythub`, `stanyslav/vebsayt-frontend`) are built locally (`docker build …`) and published before deployment.

## CI/CD

- GitHub Actions:
  - `backend-ci.yml` – installs Python deps, runs `ruff`, `black --check`, `isort --check-only`, and `manage.py check`.
  - `frontend-ci.yml` – installs Node deps, runs `npm run lint` and `npm run build`.
- Pre-commit is configured (`.pre-commit-config.yaml`) with Python and JS formatters to keep style consistent.

## Future Work

- Introduce Celery/RQ workers for async tasks.
- Add Terraform/Ansible IaC definitions.
- Extend CI with pytest and docker image build + push.
- Incorporate Stripe/YooKassa payment flows (with webhook consistency).

