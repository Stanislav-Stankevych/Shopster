from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"
    verbose_name = "Shop"

    def ready(self):
        from . import models, signals  # noqa: F401

        # Set English model names in admin to avoid mojibake
        models.Category._meta.verbose_name = "Category"
        models.Category._meta.verbose_name_plural = "Categories"
        models.Product._meta.verbose_name = "Product"
        models.Product._meta.verbose_name_plural = "Products"
        models.ProductImage._meta.verbose_name = "Product image"
        models.ProductImage._meta.verbose_name_plural = "Product images"
        models.Cart._meta.verbose_name = "Cart"
        models.Cart._meta.verbose_name_plural = "Carts"
        models.CartItem._meta.verbose_name = "Cart item"
        models.CartItem._meta.verbose_name_plural = "Cart items"
        models.Order._meta.verbose_name = "Order"
        models.Order._meta.verbose_name_plural = "Orders"
        models.OrderItem._meta.verbose_name = "Order item"
        models.OrderItem._meta.verbose_name_plural = "Order items"
        models.ProductReview._meta.verbose_name = "Product review"
        models.ProductReview._meta.verbose_name_plural = "Product reviews"
