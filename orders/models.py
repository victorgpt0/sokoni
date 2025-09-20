import uuid

from django.db import models
from django.urls import reverse

from sokoni.models import AuditTimestampModel


class Order(AuditTimestampModel):
    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("returned", "Returned"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    SHIPPING_METHOD_CHOICES = [
        ("standard", "Standard Shipping"),
        ("express", "Express Shipping"),
    ]

    order_number = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(
        "accounts.Customer", on_delete=models.CASCADE, related_name="orders"
    )

    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    shipping_address = models.ForeignKey(
        "accounts.CustomerAddress",
        on_delete=models.CASCADE,
        related_name="shipping_orders",
        null=True,
        blank=True,
    )
    billing_address = models.ForeignKey(
        "accounts.CustomerAddress",
        on_delete=models.CASCADE,
        related_name="billing_orders",
        null=True,
        blank=True,
    )
    shipping_method = models.CharField(
        max_length=20, choices=SHIPPING_METHOD_CHOICES, default="standard"
    )

    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True, default="")
    tracking_number = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Orders"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} - {self.customer.full_name} - {self.status}"

    def get_absolute_url(self):
        return reverse("orders:order_detail", args=[self.order_number])


class OrderItem(AuditTimestampModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return (
            f"{self.quantity} x {self.product_name} in Order {self.order.order_number}"
        )

    @property
    def total_price(self):
        return self.product_price * self.quantity
