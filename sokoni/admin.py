from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

# Import models for statistics
from products.models import Product, Category
from orders.models import Order, OrderItem
from payments.models import Payment
from accounts.models import Customer
from cart.models import Cart
from coupons.models import Coupon

class SokoniAdminSite(AdminSite):
    site_header = "Sokoni E-commerce Admin"
    site_title = "Sokoni Admin Portal"
    index_title = "Welcome to Sokoni Administration"
    
    def index(self, request, extra_context=None):
        """Custom admin index with statistics"""
        # Get date ranges
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        
        # Order statistics
        total_orders = Order.objects.count()
        orders_today = Order.objects.filter(created_at__date=today).count()
        orders_this_week = Order.objects.filter(created_at__date__gte=last_week).count()
        orders_this_month = Order.objects.filter(created_at__date__gte=last_month).count()
        
        # Revenue statistics
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        revenue_today = Payment.objects.filter(
            status='completed',
            paid_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        revenue_this_week = Payment.objects.filter(
            status='completed',
            paid_at__date__gte=last_week
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        revenue_this_month = Payment.objects.filter(
            status='completed',
            paid_at__date__gte=last_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Product statistics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        low_stock_products = Product.objects.filter(stock_quantity__lte=10).count()
        out_of_stock_products = Product.objects.filter(stock_quantity=0).count()
        
        # Customer statistics
        total_customers = Customer.objects.count()
        new_customers_today = Customer.objects.filter(created_at__date=today).count()
        new_customers_this_week = Customer.objects.filter(created_at__date__gte=last_week).count()
        
        # Payment statistics
        pending_payments = Payment.objects.filter(status='pending').count()
        failed_payments = Payment.objects.filter(status='failed').count()
        successful_payments = Payment.objects.filter(status='completed').count()
        
        # Recent orders
        recent_orders = Order.objects.select_related('customer__user').order_by('-created_at')[:5]
        
        # Low stock alerts
        low_stock_products_list = Product.objects.filter(stock_quantity__lte=10).order_by('stock_quantity')[:5]
        
        # Top selling products
        top_products = OrderItem.objects.values('product__name').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]
        
        # Category statistics
        category_stats = Category.objects.annotate(
            product_count=Count('products')
        ).order_by('-product_count')[:5]
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_orders': total_orders,
            'orders_today': orders_today,
            'orders_this_week': orders_this_week,
            'orders_this_month': orders_this_month,
            'total_revenue': total_revenue,
            'revenue_today': revenue_today,
            'revenue_this_week': revenue_this_week,
            'revenue_this_month': revenue_this_month,
            'total_products': total_products,
            'active_products': active_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'total_customers': total_customers,
            'new_customers_today': new_customers_today,
            'new_customers_this_week': new_customers_this_week,
            'pending_payments': pending_payments,
            'failed_payments': failed_payments,
            'successful_payments': successful_payments,
            'recent_orders': recent_orders,
            'low_stock_products_list': low_stock_products_list,
            'top_products': top_products,
            'category_stats': category_stats,
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
admin_site = SokoniAdminSite(name='sokoni_admin')

# Register all models with the custom admin site
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# Register auth models
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)

# Import and register all app models
from accounts.admin import CustomerAdmin, CustomerAddressAdmin, CustomUserAdmin
from accounts.models import Customer, CustomerAddress
from products.admin import ProductAdmin, CategoryAdmin, ProductImageAdmin, ProductReviewAdmin
from products.models import Product, Category, ProductImage, ProductReview
from orders.admin import OrderAdmin, OrderItemAdmin
from orders.models import Order, OrderItem
from payments.admin import PaymentAdmin, PaymentAttemptAdmin
from payments.models import Payment, PaymentAttempt
from cart.admin import CartAdmin, CartItemAdmin
from cart.models import Cart, CartItem
from coupons.admin import CouponAdmin
from coupons.models import Coupon

# Register all models
admin_site.register(Customer, CustomerAdmin)
admin_site.register(CustomerAddress, CustomerAddressAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(ProductImage, ProductImageAdmin)
admin_site.register(ProductReview, ProductReviewAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem, OrderItemAdmin)
admin_site.register(Payment, PaymentAdmin)
admin_site.register(PaymentAttempt, PaymentAttemptAdmin)
admin_site.register(Cart, CartAdmin)
admin_site.register(CartItem, CartItemAdmin)
admin_site.register(Coupon, CouponAdmin)

# Replace the default admin site
admin.site = admin_site

