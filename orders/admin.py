from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "total_price",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    fields = ("product", "product_name", "product_price", "quantity", "total_price")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "status",
        "payment_status",
        "total_amount",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_status",
        "created_at",
        "shipped_at",
        "delivered_at",
    )
    search_fields = (
        "order_number",
        "customer__user__username",
        "customer__user__email",
        "tracking_number",
    )
    readonly_fields = (
        "order_number",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Order Information",
            {"fields": ("order_number", "customer", "status", "payment_status")},
        ),
        (
            "Pricing",
            {
                "fields": (
                    "subtotal",
                    "tax_amount",
                    "shipping_cost",
                    "discount_amount",
                    "total_amount",
                )
            },
        ),
        (
            "Addresses",
            {
                "fields": ("billing_address", "shipping_address"),
                "classes": ("collapse",),
            },
        ),
        (
            "Additional Information",
            {"fields": ("notes", "tracking_number"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "shipped_at", "delivered_at"),
                "classes": ("collapse",),
            },
        ),
        (
            "Audit Information",
            {"fields": ("created_by", "updated_by"), "classes": ("collapse",)},
        ),
    )

    def customer_name(self, obj):
        customer_url = reverse("admin:accounts_customer_change", args=[obj.customer.pk])
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            customer_url,
            obj.customer.full_name,
            obj.customer.user.email,
        )

    customer_name.short_description = "Customer"
    customer_name.admin_order_field = "customer__user__last_name"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("customer__user")

    actions = ["mark_as_processing", "mark_as_shipped", "mark_as_delivered"]

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status="processing")
        self.message_user(request, f"{updated} orders marked as processing.")

    mark_as_processing.short_description = "Mark selected orders as processing"

    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(status="shipped", shipped_at=timezone.now())
        self.message_user(request, f"{updated} orders marked as shipped.")

    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(status="delivered", delivered_at=timezone.now())
        self.message_user(request, f"{updated} orders marked as delivered.")

    mark_as_delivered.short_description = "Mark selected orders as delivered"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "product_name",
        "product_price",
        "quantity",
        "total_price",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("order__order_number", "product__name", "product_name")
    readonly_fields = (
        "total_price",
        "created_at",
        "created_by",
        "updated_by",
        "updated_at",
    )

    fieldsets = (
        ("Order Information", {"fields": ("order",)}),
        (
            "Product Information",
            {"fields": ("product", "product_name", "product_price", "quantity")},
        ),
        ("Pricing", {"fields": ("total_price",)}),
        (
            "Timestamps",
            {"fields": ("created_at", " updated_at"), "classes": ("collapse",)},
        ),
        (
            "Audit Information",
            {"fields": ("created_by", "updated_by"), "classes": ("collapse",)},
        ),
    )

    def order_number(self, obj):
        order_url = reverse("admin:orders_order_change", args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', order_url, obj.order.order_number)

    order_number.short_description = "Order Number"
    order_number.admin_order_field = "order__order_number"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order", "product")
