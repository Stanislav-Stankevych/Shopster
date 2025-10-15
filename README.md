# Интернет-магазин на Django + DRF

## Что внутри
- Django 5 + Django REST Framework
- PostgreSQL и Redis (docker-compose)
- Базовые модели каталога, корзины и заказов
- Готовая админка с товарами, заказами и корзинами
- Gunicorn в продакшн-контейнере, статические файлы и медиа через тома

## Быстрый старт в Docker
1. Скопируйте пример переменных окружения и при необходимости измените значения:
   ```bash
   cp .env.example .env
   ```
2. Поднимите окружение:
   ```bash
   docker-compose up --build
   ```
3. Выполните начальные миграции и создайте суперпользователя (контейнер уже запускает миграции при старте, нужно только создать администратора):
   ```bash
   docker-compose exec web python backend/manage.py createsuperuser
   ```
4. Панель администратора будет доступна на `http://localhost:8000/admin/`, API — на `http://localhost:8000/api/`.

## Полезные команды
- Выполнить тесты или отдельные команды Django:
  ```bash
  docker-compose exec web python backend/manage.py <command>
  ```
- Собрать статику вручную:
  ```bash
  docker-compose exec web python backend/manage.py collectstatic --noinput
  ```

## Структура API
- `GET /api/categories/` — список категорий (анонимам только чтение, создание/изменение для админов)
- `GET /api/products/` — список товаров, включает изображения и категорию
- `POST /api/carts/` — создать корзину, `GET /api/carts/<uuid>/` — получить содержимое
- `POST /api/carts/<uuid>/items/` — добавить товар, `PATCH /api/carts/<uuid>/items/<id>/` — изменить количество, `DELETE ...` — удалить позицию
- `POST /api/orders/` — оформить заказ на основе корзины (анонимам доступно), `GET /api/orders/` — список заказов текущего пользователя (администраторы видят все)

## Деплой на сервер (общее описание)
1. Установите Docker и docker-compose plugin (или используйте `docker compose`).
2. Создайте `.env` с боевыми ключами (`DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, отключите `DJANGO_DEBUG`).
3. Настройте домен и обратный прокси (например, Nginx) на проксирование к контейнеру `web:8000`.
4. Подключите постоянное хранилище для томов `postgres_data`, `media_volume`, `static_volume`.
5. Настройте резервное копирование базы данных PostgreSQL.
6. Используйте процесс менеджер/CI для обновлений: `git pull`, `docker-compose pull`, `docker-compose up -d --build`.

## Следующие шаги
- Подключить оплату (Stripe/ЮKassa) и вебхуки оплаты.
- Добавить Celery для отложенных задач (уведомления, синхронизации).
- Добавить витрину (SPA/SSR фронтенд) или шаблонный фронт на Django.
