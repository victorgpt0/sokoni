from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Payment, PaymentAttempt


class PaymentAttemptInline(admin.TabularInline):
    model = PaymentAttempt
    extra = 0
    readonly_fields = ("paystack_reference", "status", "created_at")
    fields = ("paystack_reference", "status", "created_at")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_info",
        "amount_display",
        "payment_method",
        "status_display",
        "created_at",
        "paid_at",
    )
    list_filter = ("status", "payment_method", "created_at", "paid_at", "failed_at")
    search_fields = (
        "order__order_number",
        "order__customer__user__email",
        "order__customer__user__username",
        "paystack_reference",
    )
    readonly_fields = (
        "order",
        "amount",
        "currency",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    date_hierarchy = "created_at"
    inlines = [PaymentAttemptInline]

    fieldsets = (
        ("Order Information", {"fields": ("order",)}),
        (
            "Payment Details",
            {"fields": ("payment_method", "status", "amount", "currency")},
        ),
        (
            "Paystack Information",
            {
                "fields": (
                    "paystack_reference",
                    "paystack_access_code",
                    "paystack_transaction_id",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Payment Status", {"fields": ("paid_at", "failed_at", "failure_reason")}),
        (
            "Gateway Response",
            {"fields": ("gateway_response",), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
        (
            "Audit Information",
            {"fields": ("created_by", "updated_by"), "classes": ("collapse",)},
        ),
    )

    def order_number(self, obj):
        return format_html("<strong>{}</strong>", obj.order.order_number)

    order_number.short_description = "Order Number"
    order_number.admin_order_field = "order__order_number"

    def customer_info(self, obj):
        customer = obj.order.customer
        return format_html(
            "<strong>{}</strong><br><small>{}</small>",
            customer.full_name,
            customer.user.email,
        )

    customer_info.short_description = "Customer"

    def amount_display(self, obj):
        color = (
            "green"
            if obj.is_successful
            else "red" if obj.status == "failed" else "orange"
        )
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            f"{obj.currency} {obj.amount}",
        )

    amount_display.short_description = "Amount"
    amount_display.admin_order_field = "amount"

    def status_display(self, obj):
        status_colors = {
            "pending": "orange",
            "processing": "blue",
            "completed": "green",
            "failed": "red",
            "cancelled": "gray",
            "refunded": "purple",
        }
        color = status_colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"
    status_display.admin_order_field = "status"

    actions = [
        "mark_as_completed",
        "mark_as_failed",
        "mark_as_refunded",
        "resend_confirmation_email",
    ]

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status="completed", paid_at=timezone.now())
        self.message_user(request, f"{updated} payments marked as completed.")

    mark_as_completed.short_description = "Mark selected payments as completed"

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status="failed", failed_at=timezone.now())
        self.message_user(request, f"{updated} payments marked as failed.")

    mark_as_failed.short_description = "Mark selected payments as failed"

    def mark_as_refunded(self, request, queryset):
        updated = queryset.update(status="refunded")
        self.message_user(request, f"{updated} payments marked as refunded.")

    mark_as_refunded.short_description = "Mark selected payments as refunded"

    def resend_confirmation_email(self, request, queryset):
        from .views import send_order_confirmation_email

        count = 0
        for payment in queryset.filter(status="completed"):
            try:
                send_order_confirmation_email(payment.order, payment)
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to send email for payment {payment.id}: {e}",
                    level="ERROR",
                )
        self.message_user(request, f"Confirmation emails sent for {count} payments.")

    resend_confirmation_email.short_description = (
        "Resend confirmation emails for selected payments"
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order__customer__user")


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "payment_order",
        "paystack_reference",
        "status_display",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("payment__order__order_number", "paystack_reference")
    readonly_fields = (
        "payment",
        "paystack_reference",
        "status",
        "gateway_response",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Payment Information",
            {"fields": ("payment", "paystack_reference", "status")},
        ),
        (
            "Gateway Response",
            {"fields": ("gateway_response",), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
        (
            "Audit Information",
            {"fields": ("created_by", "updated_by"), "classes": ("collapse",)},
        ),
    )

    def payment_order(self, obj):
        return format_html(
            "<strong>{}</strong><br><small>{}</small>",
            obj.payment.order.order_number,
            obj.payment.order.customer.full_name,
        )

    payment_order.short_description = "Order"
    payment_order.admin_order_field = "payment__order__order_number"

    def status_display(self, obj):
        status_colors = {
            "success": "green",
            "failed": "red",
            "pending": "orange",
            "cancelled": "gray",
        }
        color = status_colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.title(),
        )

    status_display.short_description = "Status"
    status_display.admin_order_field = "status"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("payment__order__customer__user")
        )


# Customize admin site
admin.site.site_header = "Sokoni Admin"
admin.site.site_title = "Sokoni Admin Portal"
admin.site.index_title = "Welcome to Sokoni Administration"
