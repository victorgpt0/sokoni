from django.db import models

from sokoni.models import AuditTimestampModel


class Payment(AuditTimestampModel):
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("paystack", "Paystack"),
        ("bank_transfer", "Bank Transfer"),
        ("cash_on_delivery", "Cash on Delivery"),
    ]

    order = models.OneToOneField(
        "orders.Order", on_delete=models.CASCADE, related_name="payment"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="paystack"
    )
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )

    # Payment amounts
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")

    # Paystack specific fields
    paystack_reference = models.CharField(
        max_length=100, unique=True, blank=True, default=""
    )
    paystack_access_code = models.CharField(max_length=100, blank=True, default="")
    paystack_transaction_id = models.CharField(max_length=100, blank=True, default="")

    # Additional payment info
    gateway_response = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True, default="")

    # Timestamps
    paid_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Payment for Order {self.order.order_number} - {self.get_status_display()}"
        )

    @property
    def is_successful(self):
        return self.status == "completed"

    @property
    def is_pending(self):
        return self.status in ["pending", "processing"]


class PaymentAttempt(AuditTimestampModel):
    """Track multiple payment attempts for the same order"""

    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="attempts"
    )
    paystack_reference = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    gateway_response = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment attempt for {self.payment.order.order_number} - {self.status}"
