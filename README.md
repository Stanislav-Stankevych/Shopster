# Shopster Ј Full-stack Commerce Platform

Shopster is a production-ready ecommerce starter that pairs **Django REST Framework** + **PostgreSQL + Redis** on the backend with a **Next.js 15 / TypeScript** storefront. The stack ships with JWT authentication, Algolia search, soft-delete aware catalog management, an admin-friendly content/blog module, and SEO tooling (metadata helpers, sitemap, OpenGraph defaults).

## Architecture Snapshot

| Layer | Tech | Highlights |
| --- | --- | --- |
| Backend | Django 5, DRF, PostgreSQL, Redis, django-filter, django-taggit, django-quill-editor | Products, categories, carts, orders, SimpleJWT, password reset, soft delete, blog (Quill body, tags), SEO meta fields |
| Frontend | Next.js 15 (App Router), TypeScript, Zustand, NextAuth, Algolia InstantSearch | Catalog with filters/sorting/search, cart & checkout, account/profile forms, blog pages, dynamic metadata |
| Infra | Docker Compose, gunicorn, whitenoise | Local dev parity, `load_demo_data`, Algolia sync |

---

## Getting Started

### 1. Environment setup

```bash
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
```

Key variables (fill in as needed):

```env
# Backend
DJANGO_SECRET_KEY=change-me
POSTGRES_*  # credentials for dockerised Postgres
REDIS_PORT=6379
ALGOLIA_APP_ID=...
ALGOLIA_ADMIN_API_KEY=...
ALGOLIA_SEARCH_API_KEY=...
ALGOLIA_INDEX_NAME=shop_products
FRONTEND_PASSWORD_RESET_URL=http://localhost:3000/reset-password

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000     # backend host exposed to the browser
NEXT_PUBLIC_SITE_URL=http://localhost:3000        # used for metadata + sitemap
AUTH_SECRET=super-secret
NEXT_PUBLIC_ALGOLIA_*  # matching the backend keys
```

### 2. Launch via Docker

```bash
docker compose up --build
# create an admin for testing
docker compose exec web python backend/manage.py createsuperuser
# (optional) seed catalogue & blog
docker compose exec web python backend/manage.py load_demo_data --reset --products 120
```

Post migrate reminder:
```bash
docker compose exec web python backend/manage.py migrate
```

> `load_demo_data` now accepts `--products N` and seeds 120 SKUs by default (products, categories, images). It also works with the new search/filter pipeline.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Front routes:

- Storefront: `http://localhost:3000/`
- Auth: `/signin`, `/signup`, `/forgot-password`, `/reset-password`
- Cart & checkout: `/cart`, `/checkout`, `/checkout/success`
- Account dashboard: `/account`
- Catalog: `/products` (filters/search/sort UI)
- Blog: `/blog`, `/blog/[slug]`

---

## Backend Highlights

### Core apps
- **shop** Ч products, categories, images, carts, orders.
  - Soft-delete via `SoftDeleteModel` (products, orders). Admin actions: archive/restore/permanently delete.
  - SEO fields on products & categories (`meta_title`, `meta_description`, `meta_keywords`).
  - Filtering & sorting `/api/products/`: `?category=slug|id`, `?min_price`, `?max_price`, `?in_stock=true`, `?search=term` (handles `е/Є`, case), `?ordering=price|-price|name|-name|created_at|-created_at`.
- **accounts** Ч JWT auth (SimpleJWT), profile updates, password reset.
- **content** - blog posts with tags & Quill body.
  - Model fields: `title`, `slug`, `summary`, `body`, `tags`, `meta_*`, `og_image`, publish state (`is_published`, `published_at`).
  - Admin WYSIWYG: Quill (via django-quill-editor, customizable toolbar).

### REST API overview

Base path: `http://localhost:8000/api/`

| Endpoint | Method(s) | Notes |
| --- | --- | --- |
| `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`, `/auth/password/reset` | POST, GET/PATCH | JWT credential login, profile, password reset |
| `/products/` | GET, POST | Filter/sort; `POST` requires admin |
| `/products/<slug>/` | GET, PATCH, DELETE | Soft delete aware |
| `/categories/` | GET, POST | Includes meta fields |
| `/carts/` | POST, GET, DELETE | Returns cart with line items |
| `/carts/<uuid>/items/` | POST | Add/update/remove cart lines |
| `/orders/` | GET, POST | Checkout -> creates order, sends confirmation mail |
| `/reviews/` | GET, POST, PATCH, DELETE | Product reviews with moderation (POST доступен только покупател€м) |
| `/content/posts/` | GET, POST | `GET` returns published posts; admin sees drafts |
| `/content/posts/<slug>/` | GET, PATCH, DELETE | Detailed article body + metadata |

### Search / Algolia
- The Django app pushes updates to Algolia (see `shop/search.py` for sync logic). Use:
  ```bash
  docker compose exec web python backend/manage.py sync_algolia_products --clear
  ```
- Frontend dropdown (Algolia InstantSearch) shows 5 hits and a УShow all results (N)Ф link > goes to `/products?search=...`.

### Sitemap & robots
- `GET /sitemap.xml` aggregates products & blog posts (with `lastmod`).
- `GET /robots.txt` references the sitemap. Base URL derives from `NEXT_PUBLIC_SITE_URL` or `SITE_URL` on backend.

---

## Frontend Highlights

- **Catalog filters** (`src/components/CatalogFilters.tsx`): search term, category, price range, in-stock checkbox, ordering. Results are paginated with infinite scroll (`ProductsInfiniteList`) and always fetch fresh data when filters change.
- **Product reviews** (`src/components/ProductReviews.tsx`): на карточке товара отображаютс€ рейтинг, список отзывов с модерацией, форма создани€/редактировани€ дл€ покупателей (после совершени€ заказа).
- **SEO utilities** (`src/lib/seo.ts`): default metadata, `absoluteUrl`, `DEFAULT_OG_IMAGE`. Used in layout and page-level `generateMetadata` (product & blog pages).
- **Layout**: server-side `app/layout.tsx` with shared metadata, client-side `LayoutProviders` manages session/auth, nav (incl. blog link), search, footer.
- **Blog UI**:
  - `/blog`: paginated summaries, optional `?page=2`, `?tag=...`, `?search=`.
  - `/blog/[slug]`: detailed article (uses metadata, OG image, keywords, tags). Content is rendered from HTML produced by Quill.

---

## Admin & CMS Tips

- Django admin now has two sections:
  - **Shop**: manage products/categories (SEO fields visible in edit form, actions for archiving/restoring).
  - **Content**: create blog posts using Quill, assign tags, schedule publish (`is_published`, `published_at`).
  - Soft-deleted items remain in DB; use actions *Restore selected* or *Permanently delete*.
- Quill is bundled via `django-quill-editor`; customize toolbar/themes as needed.

---

## Useful commands (recap)

```bash
# Apply migrations
docker compose exec web python backend/manage.py migrate

# Install new deps if requirements changed
docker compose exec web pip install -r requirements.txt

# Soft-delete recovery (example)
docker compose exec web python backend/manage.py shell -c "from shop.models import Product; Product.all_objects.get(slug='slug').restore()"

# Algolia reindex
docker compose exec web python backend/manage.py sync_algolia_products

# Blog API examples
curl http://localhost:8000/api/content/posts/
curl http://localhost:8000/api/content/posts/<slug>/
```

---

## Roadmap / Ideas
- Integrate payments (Stripe/ёKassa) and webhook handlers.
- Background jobs (Celery + Redis) for email send-outs, stock sync, indexing.
- Adjust Quill modules (toolbar, themes) as needed.
- Add JSON-LD structured data for products and blog posts.
- CI/CD: automated tests, linting, image builds.


