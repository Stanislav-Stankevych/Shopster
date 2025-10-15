from __future__ import annotations

from typing import Any

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
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
