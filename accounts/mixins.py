from .models import Customer, CustomerAddress

class CustomerMixin:
    """
    Mixin to provide customer-related functionality.
    """
    
    def get_customer(self):
        """
        Returns the customer instance associated with the request user.
        """
        if not hasattr(self, 'customer'):
            self.customer, created = Customer.objects.get_or_create(user=self.request.user)

        return self.customer
    
class CustomerAddressQuerysetMixin(CustomerMixin):
    def get_queryset(self):
        return CustomerAddress.objects.filter(customer=self.get_customer())