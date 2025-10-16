from __future__ import annotations

from typing import Any

from django.conf import settings
from django.utils import timezone

from algoliasearch.search_client import SearchClient

from .models import Product

_client = None
_index = None


def get_index():
    global _client, _index
    if not settings.ALGOLIA_ENABLED:
        return None
    if _client is None:
        _client = SearchClient.create(settings.ALGOLIA_APP_ID, settings.ALGOLIA_ADMIN_API_KEY)
    if _index is None:
        _index = _client.init_index(settings.ALGOLIA_INDEX_NAME)
    return _index


def serialize_product(product: Product) -> dict[str, Any]:
    main_image = product.images.filter(is_main=True).first() or product.images.first()
    image_url = main_image.image.url if main_image else ""
    return {
        "objectID": str(product.id),
        "name": product.name,
        "slug": product.slug,
        "sku": product.sku,
        "short_description": product.short_description,
        "description": product.description,
        "price": float(product.price),
        "currency": product.currency,
        "stock": product.stock,
        "category": product.category.name if product.category else "",
        "category_slug": product.category.slug if product.category else "",
        "is_active": product.is_active,
        "updated_at": product.updated_at.isoformat() if product.updated_at else timezone.now().isoformat(),
        "image_url": image_url,
    }


def index_product(product_id: int) -> None:
    if not settings.ALGOLIA_ENABLED:
        return
    index = get_index()
    if not index:
        return
    try:
        product = (
            Product.objects.select_related("category")
            .prefetch_related("images")
            .get(pk=product_id)
        )
    except Product.DoesNotExist:
        remove_product(product_id)
        return
    if not product.is_active:
        remove_product(product_id)
        return
    index.save_object(serialize_product(product))


def remove_product(product_id: int) -> None:
    if not settings.ALGOLIA_ENABLED:
        return
    index = get_index()
    if not index:
        return
    index.delete_object(str(product_id))


def sync_all_products(clear_index: bool = False) -> None:
    if not settings.ALGOLIA_ENABLED:
        return
    index = get_index()
    if not index:
        return
    if clear_index:
        index.clear_objects()
    records = [
        serialize_product(product)
        for product in Product.objects.select_related("category").prefetch_related("images").filter(is_active=True)
    ]
    if records:
        index.save_objects(records)
