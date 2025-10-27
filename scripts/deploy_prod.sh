#!/usr/bin/env bash
set -euo pipefail

# Подготовка .env
if [ ! -f .env ]; then
  echo "Создаю .env из .env.prod.example"
  cp .env.prod.example .env
fi

# Сборка и запуск
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

docker compose -f docker-compose.prod.yml build --no-cache

docker compose -f docker-compose.prod.yml up -d

echo "\nГотово! Откройте http://localhost (или домен сервера)."
