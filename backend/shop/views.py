from __future__ import annotations

from typing import Any

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem, Category, Order, Product
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CategorySerializer,
    OrderCreateSerializer,
    OrderSerializer,
    ProductSerializer,
)

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").prefetch_related("images")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"


class CartViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Cart.objects.prefetch_related("items__product__category", "items__product__images")
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.create(
            user=request.user if request.user.is_authenticated else None,
        )
        serializer = self.get_serializer(cart)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CartItemViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        cart_id = self.kwargs["cart_id"]
        return (
            CartItem.objects.filter(cart_id=cart_id)
            .select_related("product", "cart", "product__category")
            .prefetch_related("product__images")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["cart_id"] = self.kwargs["cart_id"]
        return context

    def perform_create(self, serializer):
        cart = get_object_or_404(Cart, pk=self.kwargs["cart_id"])
        serializer.save(cart=cart)

    def perform_update(self, serializer):
        serializer.save()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = Order.objects.select_related("user").prefetch_related("items__product", "items__product__images")
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return queryset
            return queryset.filter(user=user)
        return Order.objects.none()

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = OrderSerializer(order, context=self.get_serializer_context())
        self._send_confirmation_email(order)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _send_confirmation_email(self, order: Order) -> None:
        if not order.customer_email:
            return
        try:
            items = order.items.select_related("product").all()
            lines = [
                f"- {item.product_name} x {item.quantity} - {item.line_total} {order.currency}"
                for item in items
            ]
            items_block = "\n".join(lines) if lines else "Cart is empty."
            message = (
                f"Hello, {order.shipping_full_name}!\n\n"
                f"Thank you for your order #{order.pk}.\n\n"
                f"Order summary:\n{items_block}\n\n"
                f"Subtotal: {order.subtotal_amount} {order.currency}\n"
                f"Shipping: {order.shipping_amount} {order.currency}\n"
                f"Total: {order.total_amount} {order.currency}\n\n"
                "We will contact you shortly to confirm the details.\n"
                "If you did not place this order, please ignore this email."
            )
            send_mail(
                subject=f"Order confirmation #{order.pk}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.customer_email],
                fail_silently=True,
            )
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to send order confirmation email: %s", exc)


