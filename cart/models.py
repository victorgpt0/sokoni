from django.db import models
from sokoni.models import AuditTimestampModel

class Cart(AuditTimestampModel):
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, unique=True, blank=True, null=True)

    def __str__(self):
        if self.customer:
            return f"Cart for {self.customer.full_name}"
        return f"Anonymous Cart Session: {self.session_key[:8]}...)"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
class CartItem(AuditTimestampModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"
    
    @property
    def total_price(self):
        return self.product.price * self.quantity