from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.PROTECT,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sku = models.CharField(max_length=64, unique=True)
    short_description = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def __str__(self) -> str:
        return f"{self.product.name} image"


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="carts",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self) -> str:
        return f"Cart {self.pk}"

    @property
    def subtotal(self) -> Decimal:
        total = Decimal("0.00")
        for item in self.items.select_related("product"):
            total += item.subtotal
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="cart_items",
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product")
        verbose_name = "Позиция в корзине"
        verbose_name_plural = "Позиции в корзине"

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self) -> Decimal:
        return self.product.price * self.quantity


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PENDING = "pending", "В ожидании"
        PAID = "paid", "Оплачен"
        SHIPPED = "shipped", "Отправлен"
        COMPLETED = "completed", "Завершен"
        CANCELLED = "cancelled", "Отменен"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "В ожидании"
        PAID = "paid", "Оплачен"
        REFUNDED = "refunded", "Возврат"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cart = models.OneToOneField(
        Cart,
        related_name="order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=32, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=500)
    shipping_city = models.CharField(max_length=100)
    shipping_postcode = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, default="Russia")
    notes = models.TextField(blank=True)
    placed_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-placed_at",)
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) -> str:
        return f"Order #{self.pk}"

    @classmethod
    def create_from_cart(
        cls,
        cart: Cart,
        *,
        user=None,
        shipping_amount: Decimal = Decimal("0.00"),
        currency: str = "RUB",
        **fields,
    ) -> "Order":
        with transaction.atomic():
            cart = Cart.objects.select_for_update().prefetch_related("items__product").get(pk=cart.pk)
            if not cart.items.exists():
                raise ValueError("Невозможно создать заказ из пустой корзины.")

            subtotal = Decimal("0.00")
            order = cls.objects.create(
                cart=cart,
                user=user if user and user.is_authenticated else None,
                subtotal_amount=Decimal("0.00"),
                shipping_amount=shipping_amount,
                total_amount=Decimal("0.00"),
                currency=currency,
                **fields,
            )

            order_items: list[OrderItem] = []
            for item in cart.items.select_related("product"):
                line_total = item.product.price * item.quantity
                subtotal += line_total
                order_items.append(
                    OrderItem(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        unit_price=item.product.price,
                        quantity=item.quantity,
                        line_total=line_total,
                    )
                )

            OrderItem.objects.bulk_create(order_items)

            order.subtotal_amount = subtotal
            order.total_amount = subtotal + shipping_amount
            order.save(update_fields=["subtotal_amount", "total_amount"])
            cart.delete()
            return order


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="order_items",
        on_delete=models.PROTECT,
    )
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self) -> str:
        return f"{self.product_name} x {self.quantity}"
