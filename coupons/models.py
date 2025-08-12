from django.db import models
from sokoni.models import AuditTimestampModel

class Coupon(AuditTimestampModel):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    usage_limit = models.PositiveIntegerField(blank=True, null=True)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return f"Coupon {self.code} - {self.discount_value} {self.discount_type.capitalize()}"
    
    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.valid_from or not self.valid_to:
            return False
    
        return (
            self.is_active and 
            self.valid_from <= now <= self.valid_to and 
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )
