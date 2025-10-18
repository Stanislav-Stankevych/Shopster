from __future__ import annotations

import django_filters
from django.db.models import Q, QuerySet

from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(method="filter_category")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price", "in_stock"]

    def filter_category(self, queryset: QuerySet[Product], name: str, value: str | None) -> QuerySet[Product]:
        if not value:
            return queryset
        lookup = Q(category__slug=value)
        if value.isdigit():
            lookup |= Q(category_id=value)
        return queryset.filter(lookup)

    def filter_in_stock(self, queryset: QuerySet[Product], name: str, value: bool | None) -> QuerySet[Product]:
        if value is None:
            return queryset
        if value:
            return queryset.filter(stock__gt=0)
        return queryset
