from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CartItemViewSet,
    CartViewSet,
    CategoryViewSet,
    OrderViewSet,
    ProductReviewViewSet,
    ProductViewSet,
    StatisticsOverviewView,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("carts", CartViewSet, basename="cart")
router.register("orders", OrderViewSet, basename="order")
router.register("reviews", ProductReviewViewSet, basename="review")

cart_items_list = CartItemViewSet.as_view({"get": "list", "post": "create"})
cart_items_detail = CartItemViewSet.as_view({"patch": "partial_update", "delete": "destroy"})

urlpatterns = [
    path("", include(router.urls)),
    path("carts/<uuid:cart_id>/items/", cart_items_list, name="cart-items-list"),
    path("carts/<uuid:cart_id>/items/<int:pk>/", cart_items_detail, name="cart-items-detail"),
    path("stats/overview/", StatisticsOverviewView.as_view(), name="stats-overview"),
]
