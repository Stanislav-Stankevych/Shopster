from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase

from shop.models import Cart, CartItem, Category, Order, Product


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FRONTEND_PASSWORD_RESET_URL="http://testserver/reset-password",
)
class GuestCheckoutTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name="Shoes")
        self.product = Product.objects.create(
            category=self.category,
            name="Comfort Sneaker",
            sku="SNKR-001",
            price=Decimal("4990.00"),
            stock=10,
        )
        mail.outbox = []

    def _build_cart(self) -> Cart:
        cart = Cart.objects.create()
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        return cart

    def _order_payload(self, cart: Cart, **overrides) -> dict[str, str]:
        payload: dict[str, str] = {
            "cart_id": str(cart.id),
            "customer_email": "guest@example.com",
            "customer_phone": "+7 999 000 1122",
            "shipping_full_name": "Guest Buyer",
            "shipping_address": "Lenina 1",
            "shipping_city": "Moscow",
            "shipping_postcode": "101000",
            "shipping_country": "Russia",
            "notes": "Call before delivery",
        }
        payload.update(overrides)
        return payload

    def test_guest_checkout_creates_user_and_sends_email(self):
        cart = self._build_cart()
        response = self.client.post("/api/orders/", self._order_payload(cart), format="json")

        self.assertEqual(response.status_code, 201, response.content)
        user_model = get_user_model()
        self.assertEqual(user_model.objects.filter(email="guest@example.com").count(), 1)
        user = user_model.objects.get(email="guest@example.com")
        order = Order.objects.get(pk=response.data["id"])

        self.assertEqual(order.user, user)
        self.assertFalse(user.has_usable_password())
        self.assertFalse(Cart.objects.filter(id=cart.id).exists())
        self.assertTrue(response.data["requires_account_activation"])
        self.assertEqual(response.data["activation_email"], "guest@example.com")

        self.assertEqual(len(mail.outbox), 2)
        subjects = {email.subject for email in mail.outbox}
        self.assertIn(f"Order confirmation #{order.pk}", subjects)
        self.assertIn("Добро пожаловать в Shopster", subjects)

        auto_email = next(email for email in mail.outbox if email.subject == "Добро пожаловать в Shopster")
        self.assertIn("reset-password", auto_email.body)
        self.assertEqual(auto_email.to, ["guest@example.com"])

    def test_guest_checkout_reuses_existing_user(self):
        user_model = get_user_model()
        existing_user = user_model.objects.create_user(
            username="existing-user",
            email="guest@example.com",
            password="secure-pass-123",
        )
        cart = self._build_cart()

        response = self.client.post("/api/orders/", self._order_payload(cart), format="json")

        self.assertEqual(response.status_code, 201, response.content)
        order = Order.objects.get(pk=response.data["id"])
        self.assertEqual(order.user, existing_user)
        self.assertEqual(user_model.objects.filter(email="guest@example.com").count(), 1)
        self.assertFalse(response.data["requires_account_activation"])
        self.assertNotIn("activation_email", response.data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"Order confirmation #{order.pk}")
        self.assertEqual(mail.outbox[0].to, ["guest@example.com"])
