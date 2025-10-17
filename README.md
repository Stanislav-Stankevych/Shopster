
# Shopster – Django + Next.js commerce stack

Modular e-commerce platform built with Django REST Framework, PostgreSQL, Redis, Algolia search and a Next.js 15 storefront.

## What's inside
- **Backend:** Django 5, DRF, PostgreSQL, Redis, Whitenoise for static files, JWT auth with SimpleJWT.
- **API domain:** products, categories, images, carts, orders, authentication endpoints, password reset.
- **Search:** Algolia indexing pipeline (ready to swap for Elasticsearch if required).
- **Frontend:** Next.js app router, TypeScript, Algolia InstantSearch, credential auth via NextAuth, cart & checkout (Zustand state).
- **Infrastructure:** Docker/Docker Compose, gunicorn, demo data loader, `.env` templates.

## Backend quick start (Docker)
```bash
cp .env.example .env
# Update secrets, DB passwords, Algolia keys, JWT lifetimes if needed

docker compose up --build

docker compose exec web python backend/manage.py createsuperuser
# optional demo catalogue
docker compose exec web python backend/manage.py load_demo_data --reset
```
- Admin panel: <http://localhost:8000/admin/>
- API root (products, categories, carts, orders…): <http://localhost:8000/api/>
- Auth endpoints:
  - `POST /api/auth/register/`
  - `POST /api/auth/login/` (username or email + password, returns JWT pair)
  - `POST /api/auth/refresh/`
  - `GET/PATCH /api/auth/me/`
  - `POST /api/auth/password/reset/`
  - `POST /api/auth/password/reset/confirm/`
- Cart endpoints:
  - `POST /api/carts/` — create anonymous cart
  - `GET /api/carts/<uuid>/` — fetch cart with items
  - `POST /api/carts/<uuid>/items/` — add product (or increase quantity)
  - `PATCH /api/carts/<uuid>/items/<id>/`, `DELETE ...` — update/remove line items
- Orders:
  - `POST /api/orders/` — checkout (triggers confirmation email)

### Environment highlights
```
ALGOLIA_APP_ID=...
ALGOLIA_ADMIN_API_KEY=...
ALGOLIA_SEARCH_API_KEY=...   # search-only, used by frontend
ALGOLIA_INDEX_NAME=shop_products
JWT_ACCESS_TOKEN_MINUTES=60
JWT_REFRESH_TOKEN_DAYS=7
DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DJANGO_DEFAULT_FROM_EMAIL=no-reply@example.com
FRONTEND_PASSWORD_RESET_URL=http://localhost:3000/reset-password
```
Backend automatically syncs products to Algolia on save; run a full reindex with:
```bash
docker compose exec web python backend/manage.py sync_algolia_products --clear
```
By default emails are printed to console; set `DJANGO_EMAIL_BACKEND`, SMTP credentials and `DJANGO_DEFAULT_FROM_EMAIL` for real delivery.

## Frontend (Next.js)
```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```
- Storefront: <http://localhost:3000/>
- Sign in: `/signin`
- Sign up: `/signup`
- Account dashboard (requires auth): `/account`
- Cart and checkout: `/cart`, `/checkout`, `/checkout/success`, password reset via `/forgot-password` and `/reset-password`

`AUTH_SECRET` in `.env.local` powers NextAuth session encryption. The app uses the credential provider, talking to Django's JWT endpoints. Access/refresh tokens are stored in the NextAuth JWT and refreshed automatically.  
Forgot/reset flow: `/forgot-password`, `/reset-password?uid=<uid>&token=<token>`.

## Configuration reference
- `frontend/src/lib/config.ts` – shared base URL for the Django API.
- `frontend/src/lib/authOptions.ts` - NextAuth setup, token refresh logic.
- `frontend/src/lib/cartStore.ts` - Zustand store for cart and checkout state.
- `frontend/src/app/api/auth/[...nextauth]/route.ts` - NextAuth handler.
- `frontend/src/app/cart/page.tsx`, `/checkout/page.tsx` - cart UI and checkout form.
- `frontend/src/components/AccountProfileForm.tsx` - profile update form, PATCH `/api/auth/me/`.

## Useful commands
```bash
# migrations / static assets
docker compose exec web python backend/manage.py migrate
docker compose exec web python backend/manage.py collectstatic --noinput

# demo catalogue
docker compose exec web python backend/manage.py load_demo_data --reset

# Algolia reindex
docker compose exec web python backend/manage.py sync_algolia_products

# frontend
docker compose exec web npm install
docker compose exec web npm run dev
cd frontend && npm run build
```

## Next steps
- Integrate payments (Stripe, YooKassa, etc.) and webhook processing.
- Introduce background jobs (Celery + Redis) for emails, stock sync, analytics.
- Replace Algolia with Elasticsearch/OpenSearch if you need self-hosted search.
- Automate CI/CD: tests, container builds, migrations on deploy.
