from django.contrib import admin, messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    ProductImage,
    ProductReview,
)

# Admin branding
admin.site.site_header = "Shopster Admin"
admin.site.site_title = "Shopster Admin"
admin.site.index_title = "Administration"

ORDER_STATUS_LABELS = {
    Order.Status.DRAFT: "Draft",
    Order.Status.PENDING: "Pending",
    Order.Status.PAID: "Paid",
    Order.Status.SHIPPED: "Shipped",
    Order.Status.COMPLETED: "Completed",
    Order.Status.CANCELLED: "Cancelled",
}

ORDER_PAYMENT_STATUS_LABELS = {
    Order.PaymentStatus.PENDING: "Payment pending",
    Order.PaymentStatus.PAID: "Paid",
    Order.PaymentStatus.REFUNDED: "Refunded",
}

REVIEW_MODERATION_STATUS_LABELS = {
    ProductReview.ModerationStatus.PENDING: "Pending review",
    ProductReview.ModerationStatus.APPROVED: "Approved",
    ProductReview.ModerationStatus.REJECTED: "Rejected",
}


class OrderStatusFilter(admin.SimpleListFilter):
    title = _("Status")
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return list(ORDER_STATUS_LABELS.items())

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(status=value)
        return queryset


class OrderPaymentStatusFilter(admin.SimpleListFilter):
    title = _("Payment status")
    parameter_name = "payment_status"

    def lookups(self, request, model_admin):
        return list(ORDER_PAYMENT_STATUS_LABELS.items())

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(payment_status=value)
        return queryset


class ReviewStatusFilter(admin.SimpleListFilter):
    title = _("Moderation status")
    parameter_name = "moderation_status"

    def lookups(self, request, model_admin):
        return list(REVIEW_MODERATION_STATUS_LABELS.items())

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(moderation_status=value)
        return queryset


class DeletedStatusFilter(admin.SimpleListFilter):
    title = _("Archived state")
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return (("active", _("Active")), ("archived", _("Archived")))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "archived":
            return queryset.filter(deleted_at__isnull=False)
        if value == "active":
            return queryset.filter(deleted_at__isnull=True)
        return queryset


class SoftDeleteAdmin(admin.ModelAdmin):
    actions = ["soft_delete_selected", "restore_selected", "hard_delete_selected"]

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    @admin.display(boolean=True, description=_("Archived"))
    def is_archived(self, obj):
        return obj.deleted_at is not None

    def soft_delete_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            if obj.deleted_at is None:
                obj.delete()
                count += 1
        if count:
            self.message_user(
                request,
                _("Archived %(count)d record(s).") % {"count": count},
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request, _("Selected records are already archived."), messages.WARNING
            )

    soft_delete_selected.short_description = _("Archive selected records")

    def restore_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            if obj.deleted_at:
                obj.restore()
                count += 1
        if count:
            self.message_user(
                request,
                _("Restored %(count)d record(s).") % {"count": count},
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request, _("No archived records were selected."), messages.WARNING
            )

    restore_selected.short_description = _("Restore selected records")

    def hard_delete_selected(self, request, queryset):
        count = queryset.count()
        for obj in queryset:
            obj.hard_delete()
        self.message_user(
            request,
            _("Permanently deleted %(count)d record(s).") % {"count": count},
            messages.WARNING if count else messages.INFO,
        )

    hard_delete_selected.short_description = _("Permanently delete selected records")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(SoftDeleteAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "stock",
        "is_active",
        "is_archived",
        "deleted_at",
    )
    list_filter = ("category", "is_active", DeletedStatusFilter)
    search_fields = ("name", "sku", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    readonly_fields = ("deleted_at",)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "updated_at")
    search_fields = ("id", "user__email")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "unit_price",
        "quantity",
        "line_total",
    )


@admin.register(Order)
class OrderAdmin(SoftDeleteAdmin):
    list_display = (
        "id",
        "user",
        "display_status",
        "display_payment_status",
        "total_amount",
        "placed_at",
        "is_archived",
        "deleted_at",
    )
    list_filter = (OrderStatusFilter, OrderPaymentStatusFilter, DeletedStatusFilter)
    search_fields = ("id", "customer_email", "shipping_full_name")
    readonly_fields = (
        "subtotal_amount",
        "total_amount",
        "currency",
        "placed_at",
        "updated_at",
        "deleted_at",
    )
    inlines = [OrderItemInline]

    @admin.display(description="Status")
    def display_status(self, obj: Order):
        return ORDER_STATUS_LABELS.get(obj.status, obj.status)

    @admin.display(description="Payment status")
    def display_payment_status(self, obj: Order):
        return ORDER_PAYMENT_STATUS_LABELS.get(obj.payment_status, obj.payment_status)


admin.site.register(ProductImage)
admin.site.register(CartItem)
admin.site.register(OrderItem)


@admin.register(ProductReview)
class ProductReviewAdmin(SoftDeleteAdmin):
    list_display = (
        "id",
        "product",
        "display_author",
        "user",
        "rating",
        "display_moderation_status",
        "verified_purchase",
        "is_archived",
        "created_at",
    )
    list_filter = (
        ReviewStatusFilter,
        "verified_purchase",
        DeletedStatusFilter,
        "rating",
    )
    search_fields = (
        "product__name",
        "user__email",
        "user__username",
        "author_name",
        "title",
        "body",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "moderated_at",
        "moderated_by",
        "deleted_at",
    )
    actions = SoftDeleteAdmin.actions + ["approve_reviews", "reject_reviews"]

    @admin.action(description=_("Approve selected reviews"))
    def approve_reviews(self, request, queryset):
        updated = queryset.update(
            moderation_status=ProductReview.ModerationStatus.APPROVED,
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )
        if updated:
            self.message_user(
                request,
                _("Approved %(count)d review(s).") % {"count": updated},
                messages.SUCCESS,
            )

    @admin.action(description=_("Reject selected reviews"))
    def reject_reviews(self, request, queryset):
        updated = queryset.update(
            moderation_status=ProductReview.ModerationStatus.REJECTED,
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )
        if updated:
            self.message_user(
                request,
                _("Rejected %(count)d review(s).") % {"count": updated},
                messages.WARNING,
            )

    @admin.display(description="Moderation status")
    def display_moderation_status(self, obj: ProductReview):
        return REVIEW_MODERATION_STATUS_LABELS.get(
            obj.moderation_status, obj.moderation_status
        )

    @admin.display(description=_("Author"))
    def display_author(self, obj: ProductReview):
        if obj.user_id and obj.user:
            name = obj.user.get_full_name().strip() or obj.user.get_username()
            return name
        return (obj.author_name or "").strip() or _("Guest")
