from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from .models import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    ProductImage,
)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "alt_text", "is_main")
        read_only_fields = ("id",)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "meta_title",
            "meta_description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.filter(is_active=True),
        write_only=True,
    )
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "category_id",
            "name",
            "slug",
            "sku",
            "short_description",
            "description",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "price",
            "currency",
            "stock",
            "is_active",
            "images",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.filter(is_active=True),
        write_only=True,
    )
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = ("id", "product", "product_id", "quantity", "subtotal", "cart")
        read_only_fields = ("id", "product", "subtotal", "cart")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "items", "subtotal", "total_items", "created_at", "updated_at")
        read_only_fields = fields

    def get_total_items(self, obj: Cart) -> int:
        return sum(item.quantity for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "unit_price",
            "quantity",
            "line_total",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "payment_status",
            "subtotal_amount",
            "shipping_amount",
            "total_amount",
            "currency",
            "customer_email",
            "customer_phone",
            "shipping_full_name",
            "shipping_address",
            "shipping_city",
            "shipping_postcode",
            "shipping_country",
            "notes",
            "placed_at",
            "items",
        )
        read_only_fields = (
            "id",
            "status",
            "payment_status",
            "subtotal_amount",
            "total_amount",
            "placed_at",
            "items",
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    cart_id = serializers.UUIDField(write_only=True)
    shipping_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        model = Order
        fields = (
            "cart_id",
            "customer_email",
            "customer_phone",
            "shipping_full_name",
            "shipping_address",
            "shipping_city",
            "shipping_postcode",
            "shipping_country",
            "notes",
            "shipping_amount",
        )

    def validate_cart_id(self, value):
        if not Cart.objects.filter(id=value).exists():
            raise serializers.ValidationError("Cart not found.")
        return value

    def create(self, validated_data):
        cart_id = validated_data.pop("cart_id")
        shipping_amount = validated_data.pop("shipping_amount", Decimal("0.00"))
        cart = Cart.objects.get(id=cart_id)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        try:
            order = Order.create_from_cart(
                cart,
                user=user,
                shipping_amount=shipping_amount,
                **validated_data,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return order
