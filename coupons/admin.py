from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_display",
        "minimum_amount",
        "usage_display",
        "status_display",
        "valid_period",
    )
    list_filter = ("discount_type", "is_active", "created_at", "valid_from", "valid_to")
    search_fields = ("code",)
    readonly_fields = (
        "used_count",
        "created_at",
        "is_valid",
        "created_by",
        "updated_by",
        "updated_at",
    )
    date_hierarchy = "created_at"

    fieldsets = (
        ("Coupon Information", {"fields": ("code", "is_active")}),
        (
            "Discount Settings",
            {"fields": ("discount_type", "discount_value", "minimum_amount")},
        ),
        ("Usage Limits", {"fields": ("usage_limit", "used_count")}),
        ("Validity Period", {"fields": ("valid_from", "valid_to", "is_valid")}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
        (
            "Audit Information",
            {"fields": ("created_by", "updated_by"), "classes": ("collapse",)},
        ),
    )

    def discount_display(self, obj):
        if obj.discount_type == "percentage":
            return format_html("<strong>{}%</strong>", obj.discount_value)
        else:
            return format_html("<strong>${}</strong>", obj.discount_value)

    discount_display.short_description = "Discount"
    discount_display.admin_order_field = "discount_value"

    def usage_display(self, obj):
        if obj.usage_limit:
            percentage = (obj.used_count / obj.usage_limit) * 100
            color = (
                "red" if percentage >= 90 else "orange" if percentage >= 70 else "green"
            )
            return format_html(
                '<span style="color: {};">{} / {}</span>',
                color,
                obj.used_count,
                obj.usage_limit,
            )
        return format_html('<span style="color: blue;">{} / ∞</span>', obj.used_count)

    usage_display.short_description = "Used / Limit"

    def status_display(self, obj):
        now = timezone.now()
        if not obj.is_active:
            return format_html('<span style="color: red;">Inactive</span>')
        elif now < obj.valid_from:
            return format_html('<span style="color: orange;">Not Started</span>')
        elif now > obj.valid_to:
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.usage_limit and obj.used_count >= obj.usage_limit:
            return format_html('<span style="color: red;">Usage Limit Reached</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')

    status_display.short_description = "Status"

    def valid_period(self, obj):
        return format_html(
            "{}<br><small>to</small><br>{}",
            obj.valid_from.strftime("%Y-%m-%d %H:%M"),
            obj.valid_to.strftime("%Y-%m-%d %H:%M"),
        )

    valid_period.short_description = "Valid Period"

    actions = ["activate_coupons", "deactivate_coupons", "reset_usage_count"]

    def activate_coupons(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} coupons activated.")

    activate_coupons.short_description = "Activate selected coupons"

    def deactivate_coupons(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} coupons deactivated.")

    deactivate_coupons.short_description = "Deactivate selected coupons"

    def reset_usage_count(self, request, queryset):
        updated = queryset.update(used_count=0)
        self.message_user(request, f"Usage count reset for {updated} coupons.")

    reset_usage_count.short_description = "Reset usage count for selected coupons"
