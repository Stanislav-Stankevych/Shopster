from __future__ import annotations

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Product
from .search import index_product, remove_product


@receiver(post_save, sender=Product, dispatch_uid="shop_product_algolia_sync")
def product_saved(sender, instance: Product, **kwargs):
    if not settings.ALGOLIA_ENABLED:
        return
    index_product(instance.pk)


@receiver(post_delete, sender=Product, dispatch_uid="shop_product_algolia_delete")
def product_deleted(sender, instance: Product, **kwargs):
    if not settings.ALGOLIA_ENABLED:
        return
    remove_product(instance.pk)
