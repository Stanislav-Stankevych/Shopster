# Деплой в Docker (production)

Готовая оркестрация: `docker-compose.prod.yml`. Внутри контейнеров уже будут все пакеты и программы.

## Быстрый старт

```bash
# 1) На сервере
git clone <ваш-репозиторий> app && cd app

# 2) Создайте .env (или отредактируйте секреты)
cp .env.prod.example .env

# 3) Соберите и запустите
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# 4) Откройте в браузере
http://<IP-сервера>/
```

## Что внутри
- `web` — Django + Gunicorn. В entrypoint выполняются:
  - `python manage.py migrate`
  - `python manage.py collectstatic`
- `frontend` — Next.js (production build, `npm run start`).
- `nginx` — единая точка входа: проксирует фронт, `/api/` и `/admin/` на backend.
- `db` — Postgres, `redis` — кэш.

## Переменные окружения (.env)
Смотрите `.env.prod.example` и заполните:
- `DJANGO_SECRET_KEY` — секрет Django
- `DJANGO_ALLOWED_HOSTS` — домены
- `POSTGRES_*` — параметры БД
- (опционально) `DJANGO_CORS_ALLOWED_ORIGINS`, `DJANGO_CSRF_TRUSTED_ORIGINS`

## Обновление версии
```bash
docker compose -f docker-compose.prod.yml pull   # если образы в Registry
# или build, если собираете локально на сервере
docker compose -f docker-compose.prod.yml build

docker compose -f docker-compose.prod.yml up -d
```

## Полезные команды
```bash
# Логи
docker compose -f docker-compose.prod.yml logs -f web

# Применить миграции вручную
docker compose -f docker-compose.prod.yml exec web python backend/manage.py migrate

# Создать суперпользователя
docker compose -f docker-compose.prod.yml exec web python backend/manage.py createsuperuser
```
