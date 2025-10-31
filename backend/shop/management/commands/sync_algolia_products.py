from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand

from ...search import sync_all_products


class Command(BaseCommand):
    help = "Синхронизирует все активные товары с индексом Algolia."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить индекс перед загрузкой данных.",
        )

    def handle(self, *args, **options):
        if not settings.ALGOLIA_ENABLED:
            self.stdout.write(
                self.style.WARNING(
                    "Algolia не настроена. Задайте переменные окружения и повторите."
                )
            )
            return
        clear = options["clear"]
        sync_all_products(clear_index=clear)
        self.stdout.write(
            self.style.SUCCESS("Товары синхронизированы с индексом Algolia.")
        )
