# Shopster — интернет-магазин на Django + Next.js

Модульный e-commerce стек: Django + DRF для API, PostgreSQL и Redis в Docker, фронтенд на Next.js 15, а также интеграция с Algolia для молниеносного поиска.

## Состав проекта
- **Backend:** Django 5, DRF, PostgreSQL, Redis, Celery-ready инфраструктура, Whitenoise для статики.
- **API и домен:** Каталог, изображения, корзина, заказы, REST-эндпоинты.
- **Поиск:** Синхронизация товаров в индекс Algolia (готовая команда и сигналы).
- **Frontend:** Next.js (app router, TypeScript, SSR/ISR), Algolia InstantSearch, страницы каталога, карточка товара.
- **Инфраструктура:** Docker/Docker Compose, gunicorn, миграции при старте, демо-данные, готовые env-шаблоны.

## Быстрый запуск backend (Docker)
1. Скопируйте переменные окружения и при необходимости обновите значения:
   ```bash
   cp .env.example .env
   ```
2. Запустите контейнеры:
   ```bash
   docker compose up --build
   ```
3. Создайте администратора:
   ```bash
   docker compose exec web python backend/manage.py createsuperuser
   ```
4. (Опционально) Заполните демо-данными:
   ```bash
   docker compose exec web python backend/manage.py load_demo_data --reset
   ```
5. Панель администратора — `http://localhost:8000/admin/`, API — `http://localhost:8000/api/`.

## Настройка Algolia
Задайте ключи в `.env` (backend) и `.env.local` (frontend):
```
ALGOLIA_APP_ID=...
ALGOLIA_ADMIN_API_KEY=...
ALGOLIA_SEARCH_API_KEY=...    # search-only key, используется фронтендом
ALGOLIA_INDEX_NAME=shop_products
```

Backend автоматически отправит товар в индекс при сохранении. Для полной переиндексации:
```bash
docker compose exec web python backend/manage.py sync_algolia_products --clear
```

### Elasticsearch альтернатива
Если предпочтительнее Elasticsearch/Opensearch:
1. Поднимите кластер (Docker, Managed Service).
2. Добавьте клиент (например, `opensearch-py`) и создайте индекс `products`.
3. Замените реализацию в `backend/shop/search.py` на отправку документов в Elasticsearch (bulk API).
4. Фронтенд может обращаться к вашему поисковому API (серверному) или использовать Elastic App Search/Enterprise Search.

## Frontend (Next.js 15)
1. Перейдите в каталог `frontend` и установите зависимости:
   ```bash
   cd frontend
   npm install
   ```
2. Создайте конфиг окружения:
   ```bash
   cp .env.local.example .env.local
   ```
   Обновите `NEXT_PUBLIC_API_BASE_URL` (по умолчанию `http://localhost:8000`) и параметры Algolia.
3. Запуск dev-сервера:
   ```bash
   npm run dev
   ```
   Фронтенд доступен на `http://localhost:3000/`.
4. Продакшн-сборка:
   ```bash
   npm run build
   npm run start
   ```

### Что реализовано во фронтенде
- Главная с хайлайтами и секцией «популярные товары» (данные из Django).
- Страница `/products` с карточками, интегрированным Algolia InstantSearch.
- Карточка товара `/products/[slug]`.
- Базовый дизайн, адаптивная сетка, глобальные стили на CSS.

## Синхронизация Next.js ↔ Django
- API endpoint `NEXT_PUBLIC_API_BASE_URL/api/products/` используется для SSR/ISR.
- Algolia InstantSearch получает данные напрямую из Algolia через `NEXT_PUBLIC_ALGOLIA_*`.
- Для вебхуков/интеграции можно добавить фоновые задачи (Celery + Redis) и подписаться на события оплаты/доставки.

## Полезные команды
```bash
# миграции, статика, админка
docker compose exec web python backend/manage.py migrate
docker compose exec web python backend/manage.py collectstatic --noinput

# демо-данные
docker compose exec web python backend/manage.py load_demo_data --reset

# синхронизация Algolia
docker compose exec web python backend/manage.py sync_algolia_products

# фронтенд
cd frontend && npm run dev          # dev-режим
cd frontend && npm run build        # production build
cd frontend && npm run lint         # ESLint
```

## Дальнейшие шаги
- Подключить платёжные провайдеры (Stripe, ЮKassa) и вебхуки.
- Добавить аутентификацию пользователей, wishlists, отзывы.
- Настроить CI/CD: прогон тестов, деплой контейнеров, прогрев кэшей.
- Масштабировать поиск: реплики, фильтры, персонализация Algolia или миграция на собственный кластер Elasticsearch.
