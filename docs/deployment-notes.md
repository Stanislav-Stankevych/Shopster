# Deployment Notes

## Infrastructure Overview

- **Backend**: Django 5 + Gunicorn running in container `web` (`stanyslav/vebsaythub:latest`).
- **Frontend**: Next.js 15 running in container `frontend` (`stanyslav/vebsayt-frontend:latest`).
- **Database**: PostgreSQL 16 (`postgres:16-alpine`) exposed on host port `5433`.
- **Cache**: Redis 7 (`redis:7-alpine`) exposed on host port `6379`.
- **Compose location on server**: `/srv/vebsayt/docker-compose.yml`.
- **Persistent volumes**:
  - `postgres_data` → Postgres data files.
  - `static_volume` → Django collected static files.
  - `media_volume` → Django media uploads.

## Environment Files (server)

- `/srv/vebsayt/.env` — Django/Backend configuration (database creds, JWT settings, etc.).
- `/srv/vebsayt/.env.local.frontend` — Next.js configuration (API URL, Algolia keys, auth secret).

> Сами значения переменных не храним в отчёте — доступ есть непосредственно на сервере.

## Docker Workflow

### Локальная сборка
```bash
# Собрать образы (backend + frontend) из deploy/docker-compose.yml
docker compose -f deploy/docker-compose.yml build

# Проверить локальные образы
docker images
```

### Публикация в Docker Hub
```bash
docker login

# Backend (если пересобирали локально)
docker tag deploy-web:latest stanyslav/vebsaythub:latest
docker push stanyslav/vebsaythub:latest

# Frontend
docker tag deploy-frontend:latest stanyslav/vebsayt-frontend:latest
docker push stanyslav/vebsayt-frontend:latest
```

### Обновление на сервере
```bash
ssh root@<SERVER_IP>
cd /srv/vebsayt
docker compose pull            # стянуть свежие образы
docker compose up -d           # перезапустить сервисы в фоне
docker compose ps              # убедиться, что все контейнеры running
```

### Полезные команды
```bash
# Логи
docker compose logs web | tail -n 50        # Django
docker compose logs frontend | tail -n 50   # Next.js

# Перезапуск отдельных сервисов
docker compose restart web
docker compose restart frontend

# Вход в контейнер
docker compose exec web bash
docker compose exec db psql -U POSTGRES shop
```

## Бэкап и восстановление базы

### Экспорт локальной базы
```bash
cmd /c "docker compose exec -T db pg_dump -U POSTGRES --encoding UTF8 shop > dump_local.sql"
```

### Импорт на сервер
```bash
scp dump_local.sql root@<SERVER_IP>:/srv/vebsayt/dump_local.sql
ssh root@<SERVER_IP>
cd /srv/vebsayt
docker compose stop web
docker compose exec -T db psql -U POSTGRES postgres -c 'DROP DATABASE IF EXISTS shop;'
docker compose exec -T db psql -U POSTGRES postgres -c 'CREATE DATABASE shop OWNER "POSTGRES";'
docker compose exec -T db psql -U POSTGRES shop < dump_local.sql
docker compose start web
```

## Проверка после деплоя

- Backend: `http://<SERVER_IP>:8000/` (админка `/admin/`).
- Frontend: `http://<SERVER_IP>:3000/` (каталог `/products`, блог `/blog`, поиск).
- Swagger/Docs: `http://<SERVER_IP>:8000/api/docs/`.

Убедиться, что поисковые подсказки работают (нужны корректные Algolia переменные в `.env.local.frontend`).

## Структура репозитория (ключевые файлы)

- `deploy/docker-compose.yml` — compose-конфигурация для прод-сборки.
- `frontend/Dockerfile.prod` — Dockerfile для Next.js (prod).
- `deploy/.env.prod`, `deploy/.env.local.prod` — prod конфиги (шаблоны для копирования на сервер).
- `docs/deployment-notes.md` — текущий документ.

## Примечания

- Пароли и ключи хранить в менеджере паролей или в `.env` на сервере, **не** добавлять в git.
- После изменения конфигов на сервере (например `.env.local.frontend`) обязательно перезапускать соответствующий сервис `docker compose restart <service>`.
- Если каталог `/products` или поиск отдают пустую страницу — проверь значения `NEXT_PUBLIC_API_BASE_URL` и других URL в `.env.local.frontend` (должны указывать на адрес сервера, а не localhost).
