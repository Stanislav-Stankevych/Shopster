from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"
    verbose_name = "\u041c\u0430\u0433\u0430\u0437\u0438\u043d"

    def ready(self):
        from . import models, signals  # noqa: F401

        models.Category._meta.verbose_name = "\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f"
        models.Category._meta.verbose_name_plural = "\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438"
        models.Product._meta.verbose_name = "\u0422\u043e\u0432\u0430\u0440"
        models.Product._meta.verbose_name_plural = "\u0422\u043e\u0432\u0430\u0440\u044b"
        models.ProductImage._meta.verbose_name = "\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0442\u043e\u0432\u0430\u0440\u0430"
        models.ProductImage._meta.verbose_name_plural = "\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f \u0442\u043e\u0432\u0430\u0440\u0430"
        models.Cart._meta.verbose_name = "\u041a\u043e\u0440\u0437\u0438\u043d\u0430"
        models.Cart._meta.verbose_name_plural = "\u041a\u043e\u0440\u0437\u0438\u043d\u044b"
        models.CartItem._meta.verbose_name = "\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u043a\u043e\u0440\u0437\u0438\u043d\u044b"
        models.CartItem._meta.verbose_name_plural = "\u041f\u043e\u0437\u0438\u0446\u0438\u0438 \u043a\u043e\u0440\u0437\u0438\u043d\u044b"
        models.Order._meta.verbose_name = "\u0417\u0430\u043a\u0430\u0437"
        models.Order._meta.verbose_name_plural = "\u0417\u0430\u043a\u0430\u0437\u044b"
        models.OrderItem._meta.verbose_name = "\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0437\u0430\u043a\u0430\u0437\u0430"
        models.OrderItem._meta.verbose_name_plural = "\u041f\u043e\u0437\u0438\u0446\u0438\u0438 \u0437\u0430\u043a\u0430\u0437\u0430"
        models.ProductReview._meta.verbose_name = "\u041e\u0442\u0437\u044b\u0432 \u043e \u0442\u043e\u0432\u0430\u0440\u0435"
        models.ProductReview._meta.verbose_name_plural = "\u041e\u0442\u0437\u044b\u0432\u044b \u043e \u0442\u043e\u0432\u0430\u0440\u0430\u0445"
