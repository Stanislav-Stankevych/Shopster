from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from .models import Cart, CartItem, Category, Order, OrderItem, Product, ProductImage


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
            self.message_user(request, _("Archived %(count)d record(s).") % {"count": count}, messages.SUCCESS)
        else:
            self.message_user(request, _("Selected records are already archived."), messages.WARNING)

    soft_delete_selected.short_description = _("Archive selected records")

    def restore_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            if obj.deleted_at:
                obj.restore()
                count += 1
        if count:
            self.message_user(request, _("Restored %(count)d record(s).") % {"count": count}, messages.SUCCESS)
        else:
            self.message_user(request, _("No archived records were selected."), messages.WARNING)

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
    list_display = ("name", "sku", "category", "price", "stock", "is_active", "is_archived", "deleted_at")
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
    readonly_fields = ("product", "product_name", "unit_price", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(SoftDeleteAdmin):
    list_display = ("id", "user", "status", "payment_status", "total_amount", "placed_at", "is_archived", "deleted_at")
    list_filter = ("status", "payment_status", DeletedStatusFilter)
    search_fields = ("id", "customer_email", "shipping_full_name")
    readonly_fields = ("subtotal_amount", "total_amount", "currency", "placed_at", "updated_at", "deleted_at")
    inlines = [OrderItemInline]


admin.site.register(ProductImage)
admin.site.register(CartItem)
admin.site.register(OrderItem)
