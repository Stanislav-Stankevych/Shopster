from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from shop.models import Category, Order, OrderItem, Product, ProductReview


class ProductReviewAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="secret",
            first_name="Buyer",
            last_name="User",
        )
        self.other_user = get_user_model().objects.create_user(
            username="guest",
            email="guest@example.com",
            password="secret",
        )
        self.staff = get_user_model().objects.create_user(
            username="moderator",
            email="mod@example.com",
            password="secret",
            is_staff=True,
        )
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            category=self.category,
            name="Test Gadget",
            sku="TG-001",
            price=Decimal("199.99"),
            stock=10,
        )
        self.order = Order.objects.create(
            user=self.user,
            cart=None,
            status=Order.Status.COMPLETED,
            payment_status=Order.PaymentStatus.PAID,
            subtotal_amount=Decimal("199.99"),
            shipping_amount=Decimal("0.00"),
            total_amount=Decimal("199.99"),
            currency="RUB",
            customer_email=self.user.email,
            shipping_full_name="Buyer User",
            shipping_address="Main street 1",
            shipping_city="Moscow",
            shipping_postcode="101000",
            shipping_country="Russia",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            unit_price=self.product.price,
            quantity=1,
            line_total=self.product.price,
        )

    def test_user_with_purchase_can_create_review(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("review-list"),
            {
                "product_id": self.product.id,
                "rating": 5,
                "title": "Отличный товар",
                "body": "Все понравилось",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = ProductReview.objects.with_unapproved().get()
        self.assertTrue(review.verified_purchase)
        self.assertEqual(
            review.moderation_status, ProductReview.ModerationStatus.PENDING
        )

    def test_user_without_purchase_can_create_review(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.post(
            reverse("review-list"),
            {
                "product_id": self.product.id,
                "rating": 4,
                "title": "Хочу оставить отзыв",
                "body": "Но покупку не совершал",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = ProductReview.objects.with_unapproved().get()
        self.assertFalse(review.verified_purchase)
        self.assertEqual(review.user, self.other_user)
        self.assertEqual(review.author_name, self.other_user.get_username())

    def test_anonymous_user_can_create_review(self):
        response = self.client.post(
            reverse("review-list"),
            {
                "product_id": self.product.id,
                "rating": 5,
                "body": "Гость делится впечатлением",
                "author_name": "Свободный гость",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = ProductReview.objects.with_unapproved().get()
        self.assertIsNone(review.user)
        self.assertEqual(review.author_name, "Свободный гость")
        self.assertFalse(review.verified_purchase)
        self.assertEqual(
            review.moderation_status, ProductReview.ModerationStatus.PENDING
        )
        self.assertIsNone(response.data["user"]["id"])
        self.assertEqual(response.data["user"]["name"], "Свободный гость")

    def test_pending_review_visible_only_to_author(self):
        self.client.force_authenticate(self.user)
        self.client.post(
            reverse("review-list"),
            {
                "product_id": self.product.id,
                "rating": 5,
                "body": "Замечательно",
            },
            format="json",
        )
        self.client.force_authenticate(user=None)
        public_response = self.client.get(
            reverse("review-list"), {"product": self.product.id}, format="json"
        )
        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(public_response.data["count"], 0)

        self.client.force_authenticate(self.user)
        author_response = self.client.get(
            reverse("review-list"), {"product": self.product.id}, format="json"
        )
        self.assertEqual(author_response.data["count"], 1)

    def test_staff_can_moderate_review(self):
        self.client.force_authenticate(self.user)
        create_response = self.client.post(
            reverse("review-list"),
            {
                "product_id": self.product.id,
                "rating": 5,
                "body": "Стоит своих денег",
            },
            format="json",
        )
        review_id = create_response.data["id"]
        self.client.force_authenticate(self.staff)
        response = self.client.post(
            reverse("review-moderate", args=[review_id]),
            {"status": ProductReview.ModerationStatus.APPROVED, "note": "OK"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review = ProductReview.objects.with_unapproved().get(id=review_id)
        self.assertEqual(
            review.moderation_status, ProductReview.ModerationStatus.APPROVED
        )
        self.assertEqual(review.moderated_by, self.staff)
        self.assertEqual(review.moderation_note, "OK")

    def test_update_resets_moderation(self):
        self.client.force_authenticate(self.user)
        create_response = self.client.post(
            reverse("review-list"),
            {
                "product_id": self.product.id,
                "rating": 4,
                "body": "Неплохой",
            },
            format="json",
        )
        review_id = create_response.data["id"]

        self.client.force_authenticate(self.staff)
        self.client.post(
            reverse("review-moderate", args=[review_id]),
            {"status": ProductReview.ModerationStatus.APPROVED},
            format="json",
        )

        self.client.force_authenticate(self.user)
        update_response = self.client.patch(
            reverse("review-detail", args=[review_id]),
            {"body": "Обновленный отзыв", "rating": 5},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        review = ProductReview.objects.with_unapproved().get(id=review_id)
        self.assertEqual(
            review.moderation_status, ProductReview.ModerationStatus.PENDING
        )
        self.assertIsNone(review.moderated_by)

    def test_product_detail_contains_rating_and_flags(self):
        product_url = reverse("product-detail", args=[self.product.slug])

        self.client.force_authenticate(self.user)
        initial = self.client.get(product_url, format="json").data
        self.assertTrue(initial["can_review"])
        self.assertIsNone(initial["user_review"])
        self.assertIsNone(initial["average_rating"])
        self.assertEqual(initial["reviews_count"], 0)

        create_response = self.client.post(
            reverse("review-list"),
            {
                "product_id": self.product.id,
                "rating": 5,
                "body": "Люблю этот товар",
            },
            format="json",
        )
        review_id = create_response.data["id"]

        after_create = self.client.get(product_url, format="json").data
        self.assertFalse(after_create["can_review"])
        self.assertIsNotNone(after_create["user_review"])
        self.assertEqual(after_create["reviews_count"], 0)
        self.assertIsNone(after_create["average_rating"])

        self.client.force_authenticate(self.staff)
        self.client.post(
            reverse("review-moderate", args=[review_id]),
            {"status": ProductReview.ModerationStatus.APPROVED},
            format="json",
        )

        self.client.force_authenticate(self.user)
        after_moderation = self.client.get(product_url, format="json").data
        self.assertFalse(after_moderation["can_review"])
        self.assertEqual(after_moderation["reviews_count"], 1)
        self.assertEqual(after_moderation["average_rating"], 5.0)
