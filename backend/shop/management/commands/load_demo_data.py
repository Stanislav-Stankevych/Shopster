from __future__ import annotations

import random
from dataclasses import dataclass
from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from ...models import Cart, CartItem, Category, Order, OrderItem, Product, ProductImage


@dataclass
class ProductSeed:
    name: str
    category: str
    price: Decimal
    currency: str
    description: str
    short_description: str
    stock: int
    sku: str
    color: tuple[int, int, int]


CATEGORIES: dict[str, str] = {
    "Электроника": "Последние модели смартфонов, ноутбуков и наушников для любых задач.",
    "Дом и уют": "Товары для организации пространства, декор и освещение.",
    "Красота и здоровье": "Уходовые средства, гаджеты для здоровья и красоты.",
    "Спорт и активный отдых": "Экипировка и аксессуары для тренировок и путешествий.",
    "Кухня и техника": "Бытовая техника и посуда для приготовления вкусных блюд.",
}

PRODUCTS: list[ProductSeed] = [
    ProductSeed(
        name="Смартфон Nova X20",
        category="Электроника",
        price=Decimal("45990"),
        currency="RUB",
        description="Флагманский смартфон с экраном 6.7\" AMOLED 120 Гц, тройной камерой 108 Мп и поддержкой 5G.",
        short_description="Флагманский смартфон 2025 года.",
        stock=25,
        sku="NX20-BLK-256",
        color=(37, 99, 235),
    ),
    ProductSeed(
        name="Беспроводные наушники AirTune Pro",
        category="Электроника",
        price=Decimal("12990"),
        currency="RUB",
        description="Активное шумоподавление, до 36 часов автономной работы, поддержка беспроводной зарядки.",
        short_description="Наушники с ANC и прозрачным режимом.",
        stock=80,
        sku="AT-PRO-WHT",
        color=(14, 116, 144),
    ),
    ProductSeed(
        name="Умная лампа Aurora Glow",
        category="Дом и уют",
        price=Decimal("3490"),
        currency="RUB",
        description="Виртуозная подсветка с миллионом оттенков, управлением через приложение и голосовых ассистентов.",
        short_description="Лампа с RGB и сценами освещения.",
        stock=120,
        sku="AGLOW-01",
        color=(99, 102, 241),
    ),
    ProductSeed(
        name="Аромадиффузор Breeze",
        category="Дом и уют",
        price=Decimal("2590"),
        currency="RUB",
        description="Компактный ультразвуковой диффузор на 200 мл, автоотключение и подсветка.",
        short_description="Увлажняет и наполняет дом ароматом.",
        stock=60,
        sku="BRZ-200",
        color=(2, 132, 199),
    ),
    ProductSeed(
        name="Фитнес-браслет PulseTrack 4",
        category="Спорт и активный отдых",
        price=Decimal("5990"),
        currency="RUB",
        description="Оптический датчик пульса, мониторинг сна, более 100 тренировок и NFC-оплата.",
        short_description="Твой помощник для активной жизни.",
        stock=150,
        sku="PT4-ONYX",
        color=(34, 197, 94),
    ),
    ProductSeed(
        name="Йогамат Balance Pro 6 мм",
        category="Спорт и активный отдых",
        price=Decimal("2190"),
        currency="RUB",
        description="Противоскользящая поверхность, усиленная плотность, в комплекте чехол и ремень.",
        short_description="Универсальный коврик для тренировок.",
        stock=95,
        sku="YOGA-BP-6",
        color=(249, 115, 22),
    ),
    ProductSeed(
        name="Блендер FreshMix 900",
        category="Кухня и техника",
        price=Decimal("7990"),
        currency="RUB",
        description="Мощность 900 Вт, 5 режимов скорости, чаша из боросиликатного стекла 1.5 л.",
        short_description="Смузи, крем-супы и соусы за минуты.",
        stock=40,
        sku="FMX-900",
        color=(220, 38, 38),
    ),
    ProductSeed(
        name="Умная зубная щётка SmileCare Sonic",
        category="Красота и здоровье",
        price=Decimal("3990"),
        currency="RUB",
        description="40 000 вибраций в минуту, 4 режима чистки, приложение для отслеживания прогресса.",
        short_description="Чистка как в кабинете стоматолога.",
        stock=70,
        sku="SC-SONIC",
        color=(217, 70, 239),
    ),
]


def generate_image_bytes(product_name: str, color: tuple[int, int, int]) -> ContentFile:
    """Create a simple placeholder image containing product name."""
    width, height = 960, 640
    image = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 42)
    except OSError:
        font = ImageFont.load_default()
    text = product_name[:32]
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((width - text_width) / 2, (height - text_height) / 2)
    draw.text(position, text, fill=(255, 255, 255), font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    filename = f"{slugify(product_name)}.png"
    return ContentFile(buffer.read(), name=filename)


class Command(BaseCommand):
    help = "Заполняет магазин демонстрационными категориями, товарами и изображениями."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Удалить существующие данные магазина перед загрузкой демо.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Очищаю существующие данные магазина..."))
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            CartItem.objects.all().delete()
            Cart.objects.all().delete()
            ProductImage.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()

        created_categories = self._create_categories()
        created_products = self._create_products(created_categories)

        self.stdout.write(self.style.SUCCESS(f"Готово! Категорий: {len(created_categories)}, товаров: {len(created_products)}"))
        self.stdout.write("Теперь можно открыть главную страницу http://localhost:8000/ и увидеть витрину.")

    def _create_categories(self) -> dict[str, Category]:
        categories: dict[str, Category] = {}
        for name, description in CATEGORIES.items():
            category, _ = Category.objects.update_or_create(
                name=name,
                defaults={"description": description, "is_active": True},
            )
            categories[name] = category
        return categories

    def _create_products(self, categories: dict[str, Category]) -> list[Product]:
        created_products: list[Product] = []
        for seed in PRODUCTS:
            category = categories[seed.category]
            product, _ = Product.objects.update_or_create(
                sku=seed.sku,
                defaults={
                    "category": category,
                    "name": seed.name,
                    "short_description": seed.short_description,
                    "description": seed.description,
                    "price": seed.price,
                    "currency": seed.currency,
                    "stock": seed.stock,
                    "is_active": True,
                },
            )

            # regenerate images
            product.images.all().delete()
            image_file = generate_image_bytes(seed.name, seed.color)
            ProductImage.objects.create(product=product, image=image_file, alt_text=seed.name, is_main=True)

            created_products.append(product)
        return created_products
