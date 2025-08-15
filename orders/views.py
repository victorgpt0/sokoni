from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from decimal import Decimal
import uuid

from .models import Order, OrderItem
from cart.models import Cart, CartItem
from cart.views import get_or_create_cart
from accounts.models import CustomerAddress
from coupons.views import apply_coupon_to_order, use_coupon
from products.models import Product

@login_required
def checkout_view(request):
    """Checkout page"""
    cart = get_or_create_cart(request)
    cart_items = cart.cart_items.select_related('product').prefetch_related('product__images')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart_detail')
    
    # Check stock availability
    for item in cart_items:
        if item.quantity > item.product.stock_quantity:
            messages.error(request, f'Only {item.product.stock_quantity} of {item.product.name} available')
            return redirect('cart:cart_detail')
        if not item.product.is_active:
            messages.error(request, f'{item.product.name} is no longer available')
            return redirect('cart:cart_detail')
    
    # Get customer addresses
    shipping_addresses = CustomerAddress.objects.filter(
        customer=request.user.customer,
        type='shipping'
    ).order_by('-is_default', '-created_at')
    
    billing_addresses = CustomerAddress.objects.filter(
        customer=request.user.customer,
        type='billing'
    ).order_by('-is_default', '-created_at')
    
    # Calculate totals
    subtotal = cart.subtotal
    tax_amount = subtotal * settings.TAX_RATE
    
    # Shipping calculation
    shipping_cost = Decimal('0.00')
    if subtotal < settings.FREE_SHIPPING_THRESHOLD:
        shipping_cost = settings.DEFAULT_SHIPPING_COST
    
    # Apply coupon if exists
    discount_amount = Decimal('0.00')
    applied_coupon_code = request.session.get('applied_coupon_code')
    if applied_coupon_code:
        is_valid, discount, error = apply_coupon_to_order(applied_coupon_code, subtotal)
        if is_valid:
            discount_amount = discount
        else:
            # Remove invalid coupon from session
            del request.session['applied_coupon_code']
            messages.warning(request, f'Coupon removed: {error}')
    
    total_amount = subtotal + tax_amount + shipping_cost - discount_amount
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'shipping_addresses': shipping_addresses,
        'billing_addresses': billing_addresses,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'shipping_cost': shipping_cost,
        'discount_amount': discount_amount,
        'total_amount': total_amount,
        'applied_coupon_code': applied_coupon_code,
        'free_shipping_threshold': settings.FREE_SHIPPING_THRESHOLD,
        'default_shipping_cost': settings.DEFAULT_SHIPPING_COST,
        'express_shipping_cost': Decimal('1000.00'),  # Express shipping cost
        'free_shipping_remaining': max(0, settings.FREE_SHIPPING_THRESHOLD - subtotal),
        'tax_rate': settings.TAX_RATE,
    }
    
    return render(request, 'orders/checkout.html', context)

@login_required
@transaction.atomic
def create_order_view(request):
    """Create order from cart"""
    if request.method != 'POST':
        return redirect('orders:checkout')
    
    cart = get_or_create_cart(request)
    cart_items = cart.cart_items.select_related('product')
    
    if not cart_items.exists():
        error_msg = 'Your cart is empty'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('cart:cart_detail')
    
    # Get addresses
    shipping_address_id = request.POST.get('shipping_address')
    billing_address_id = request.POST.get('billing_address')
    
    if not shipping_address_id or not billing_address_id:
        error_msg = 'Please select both shipping and billing addresses'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('orders:checkout')
    
    try:
        shipping_address = CustomerAddress.objects.get(
            id=shipping_address_id,
            customer=request.user.customer,
            type='shipping'
        )
        billing_address = CustomerAddress.objects.get(
            id=billing_address_id,
            customer=request.user.customer,
            type='billing'
        )
    except CustomerAddress.DoesNotExist:
        error_msg = 'Invalid address selected'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('orders:checkout')
    
    # Validate cart items and calculate totals
    subtotal = Decimal('0.00')
    for item in cart_items:
        if item.quantity > item.product.stock_quantity:
            messages.error(request, f'Insufficient stock for {item.product.name}')
            return redirect('cart:cart_detail')
        if not item.product.is_active:
            messages.error(request, f'{item.product.name} is no longer available')
            return redirect('cart:cart_detail')
        subtotal += item.total_price
    
    # Get shipping method
    shipping_method = request.POST.get('shipping_method', 'standard')
    
    # Calculate other amounts
    tax_amount = subtotal * settings.TAX_RATE
    
    # Calculate shipping cost based on method
    if shipping_method == 'express':
        shipping_cost = Decimal('1000.00')  # Express shipping
    else:
        # Standard shipping
        shipping_cost = Decimal('0.00')
        if subtotal < settings.FREE_SHIPPING_THRESHOLD:
            shipping_cost = settings.DEFAULT_SHIPPING_COST
    
    # Apply coupon
    discount_amount = Decimal('0.00')
    applied_coupon_code = request.session.get('applied_coupon_code')
    if applied_coupon_code:
        is_valid, discount, error = apply_coupon_to_order(applied_coupon_code, subtotal)
        if is_valid:
            discount_amount = discount
        else:
            messages.error(request, f'Coupon error: {error}')
            return redirect('orders:checkout')
    
    total_amount = subtotal + tax_amount + shipping_cost - discount_amount
    
    # Create order
    order = Order.objects.create(
        customer=request.user.customer,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_cost=shipping_cost,
        discount_amount=discount_amount,
        total_amount=total_amount,
        shipping_address=shipping_address,
        billing_address=billing_address,
        shipping_method=shipping_method,
        status='pending',
        payment_status='pending'
    )
    
    # Create order items and update stock
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            product_name=cart_item.product.name,
            product_price=cart_item.product.price,
            quantity=cart_item.quantity
        )
        
        # Update product stock
        product = cart_item.product
        product.stock_quantity -= cart_item.quantity
        product.save()
    
    # Mark coupon as used
    if applied_coupon_code:
        use_coupon(applied_coupon_code)
        del request.session['applied_coupon_code']
    
    # Clear cart
    cart.cart_items.all().delete()
    
    # Store order in session for payment
    request.session['pending_order_id'] = order.id
    
    messages.success(request, f'Order {order.order_number} created successfully!')
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'payment_url': reverse('payments:process_payment', args=[order.order_number])
        })
    
    # Redirect to payment
    return redirect('payments:process_payment', order_number=order.order_number)

class OrderHistoryView(LoginRequiredMixin, ListView):
    """Order history page"""
    model = Order
    template_name = 'accounts/orders/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(
            customer=self.request.user.customer
        ).prefetch_related('order_items__product').order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    """Order detail page"""
    model = Order
    template_name = 'accounts/orders/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        return Order.objects.filter(
            customer=self.request.user.customer
        ).prefetch_related('order_items__product')

@login_required
def cancel_order_view(request, order_number):
    """Cancel an order"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        customer=request.user.customer
    )
    
    if order.status not in ['pending', 'processing']:
        messages.error(request, 'This order cannot be cancelled')
        return redirect('accounts:order_detail', order_number=order_number)
    
    if request.method == 'POST':
        # Restore stock
        for item in order.order_items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
        
        # Update order status
        order.status = 'cancelled'
        order.payment_status = 'failed'
        order.save()
        
        messages.success(request, f'Order {order_number} has been cancelled')
        return redirect('accounts:order_history')
    
    return render(request, 'orders/cancel_order.html', {'order': order})

@login_required
def reorder_view(request, order_number):
    """Reorder items from a previous order"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        customer=request.user.customer
    )
    
    cart = get_or_create_cart(request)
    added_items = []
    unavailable_items = []
    
    for order_item in order.order_items.all():
        product = order_item.product
        
        # Check if product is still available
        if not product.is_active or product.stock_quantity < 1:
            unavailable_items.append(product.name)
            continue
        
        # Add to cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': min(order_item.quantity, product.stock_quantity)}
        )
        
        if not created:
            # Update existing cart item
            new_quantity = min(
                cart_item.quantity + order_item.quantity,
                product.stock_quantity,
                settings.CART_ITEM_MAX_QUANTITY
            )
            cart_item.quantity = new_quantity
            cart_item.save()
        
        added_items.append(product.name)
    
    if added_items:
        messages.success(request, f'Added {len(added_items)} items to your cart')
    
    if unavailable_items:
        messages.warning(request, f'Some items are no longer available: {", ".join(unavailable_items)}')
    
    return redirect('cart:cart_detail')

def order_tracking_view(request, order_number):
    """Public order tracking (no login required)"""
    email = request.GET.get('email')
    
    if not email:
        return render(request, 'orders/track_order_form.html')
    
    try:
        order = Order.objects.get(
            order_number=order_number,
            customer__user__email=email
        )
        
        # Order status timeline
        status_timeline = []
        if order.created_at:
            status_timeline.append({
                'status': 'Order Placed',
                'date': order.created_at,
                'completed': True,
                'description': 'Your order has been received and is being processed'
            })
        
        if order.status in ['processing', 'shipped', 'delivered']:
            status_timeline.append({
                'status': 'Processing',
                'date': order.updated_at,
                'completed': True,
                'description': 'Your order is being prepared for shipment'
            })
        
        if order.shipped_at:
            status_timeline.append({
                'status': 'Shipped',
                'date': order.shipped_at,
                'completed': True,
                'description': f'Your order has been shipped. Tracking: {order.tracking_number or "N/A"}'
            })
        
        if order.delivered_at:
            status_timeline.append({
                'status': 'Delivered',
                'date': order.delivered_at,
                'completed': True,
                'description': 'Your order has been delivered'
            })
        
        context = {
            'order': order,
            'status_timeline': status_timeline,
        }
        
        return render(request, 'orders/track_order.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found. Please check your order number and email.')
        return render(request, 'orders/track_order_form.html')

def order_invoice_view(request, order_number):
    """Generate order invoice"""
    if request.user.is_authenticated:
        order = get_object_or_404(
            Order,
            order_number=order_number,
            customer=request.user.customer
        )
    else:
        # For guest users, require email verification
        email = request.GET.get('email')
        if not email:
            messages.error(request, 'Email required to view invoice')
            return redirect('orders:track_order', order_number=order_number)
        
        order = get_object_or_404(
            Order,
            order_number=order_number,
            customer__user__email=email
        )
    
    context = {
        'order': order,
        'company_name': 'Sokoni',
        'company_address': 'Nairobi, Kenya',  # Update with actual address
    }
    
    return render(request, 'orders/invoice.html', context)