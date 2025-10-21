from __future__ import annotations

from django.db.models import Q

from .models import Order, OrderItem, Product


def user_has_verified_purchase(user, product: Product) -> bool:
    if not user or not user.is_authenticated:
        return False
    qualifying_statuses = {
        Order.Status.PAID,
        Order.Status.SHIPPED,
        Order.Status.COMPLETED,
    }
    qualifying_payments = {
        Order.PaymentStatus.PAID,
    }
    return OrderItem.objects.filter(
        order__user=user,
        order__deleted_at__isnull=True,
        order__status__in=qualifying_statuses,
        order__payment_status__in=qualifying_payments,
        product=product,
    ).exists()
