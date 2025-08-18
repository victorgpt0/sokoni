from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
import json

from .models import Coupon

def validate_coupon_api(request):
    """API endpoint to validate coupon"""
    coupon_code = request.GET.get('code', '').strip().upper()
    cart_total = request.GET.get('cart_total', '0')
    
    if not coupon_code:
        return JsonResponse({
            'valid': False,
            'error': 'Coupon code is required'
        })
    
    try:
        cart_total = Decimal(cart_total)
    except:
        cart_total = Decimal('0')
    
    try:
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        
        # Check validity
        if not coupon.is_valid:
            return JsonResponse({
                'valid': False,
                'error': 'This coupon has expired or is not active'
            })
        
        # Check minimum amount
        if cart_total < coupon.minimum_amount:
            return JsonResponse({
                'valid': False,
                'error': f'Minimum order amount of KES {coupon.minimum_amount} required'
            })
        
        # Check usage limit
        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            return JsonResponse({
                'valid': False,
                'error': 'This coupon has reached its usage limit'
            })
        
        # Calculate discount
        if coupon.discount_type == 'percentage':
            discount_amount = cart_total * (coupon.discount_value / 100)
            discount_text = f'{coupon.discount_value}% off'
        else:
            discount_amount = coupon.discount_value
            discount_text = f'KES {coupon.discount_value} off'
        
        return JsonResponse({
            'valid': True,
            'discount_amount': str(discount_amount),
            'discount_text': discount_text,
            'coupon_type': coupon.discount_type,
            'coupon_value': str(coupon.discount_value),
            'message': f'Coupon "{coupon_code}" applied successfully!'
        })
        
    except Coupon.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'error': 'Invalid coupon code'
        })

@staff_member_required
def coupon_list_view(request):
    """Admin view to list all coupons"""
    coupons = Coupon.objects.all().order_by('-created_at')
    
    # Search filter
    search_query = request.GET.get('search')
    if search_query:
        coupons = coupons.filter(
            Q(code__icontains=search_query) |
            Q(discount_type__icontains=search_query)
        )
    
    # Status filter
    status = request.GET.get('status')
    if status == 'active':
        coupons = coupons.filter(is_active=True)
    elif status == 'expired':
        now = timezone.now()
        coupons = coupons.filter(
            Q(valid_to__lt=now) | Q(is_active=False)
        )
    elif status == 'used_up':
        coupons = [c for c in coupons if c.usage_limit and c.used_count >= c.usage_limit]
    
    context = {
        'coupons': coupons,
        'search_query': search_query,
        'status_filter': status,
    }
    
    return render(request, 'coupons/coupon_list.html', context)

@staff_member_required
def coupon_stats_view(request, coupon_id):
    """View coupon usage statistics"""
    coupon = get_object_or_404(Coupon, id=coupon_id)
    
    # Get usage statistics
    stats = {
        'total_uses': coupon.used_count,
        'remaining_uses': (coupon.usage_limit - coupon.used_count) if coupon.usage_limit else 'Unlimited',
        'usage_percentage': (coupon.used_count / coupon.usage_limit * 100) if coupon.usage_limit else 0,
        'is_active': coupon.is_active,
        'is_expired': timezone.now() > coupon.valid_to if coupon.valid_to else False,
        'days_remaining': (coupon.valid_to - timezone.now()).days if coupon.valid_to and coupon.valid_to > timezone.now() else 0,
    }
    
    context = {
        'coupon': coupon,
        'stats': stats,
    }
    
    return render(request, 'coupons/coupon_stats.html', context)

def apply_coupon_to_order(coupon_code, order_total):
    """
    Helper function to apply coupon discount to an order
    Returns (is_valid, discount_amount, error_message)
    """
    try:
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        
        if not coupon.is_valid:
            return False, 0, 'Coupon has expired or is not active'
        
        if order_total < coupon.minimum_amount:
            return False, 0, f'Minimum order amount of KES {coupon.minimum_amount} required'
        
        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            return False, 0, 'Coupon usage limit reached'
        
        # Calculate discount
        if coupon.discount_type == 'percentage':
            discount_amount = order_total * (coupon.discount_value / 100)
        else:
            discount_amount = min(coupon.discount_value, order_total)
        
        return True, discount_amount, ''
        
    except Coupon.DoesNotExist:
        return False, 0, 'Invalid coupon code'

def use_coupon(coupon_code):
    """
    Mark coupon as used (increment usage count)
    Call this after successful order completion
    """
    try:
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        coupon.used_count += 1
        coupon.save()
        return True
    except Coupon.DoesNotExist:
        return False

@require_POST
def apply_coupon_view(request):
    """Apply coupon to cart"""
    try:
        data = json.loads(request.body)
        coupon_code = data.get('code', '').strip().upper()
        cart_total = data.get('cart_total', '0')
        
        if not coupon_code:
            return JsonResponse({
                'success': False,
                'error': 'Coupon code is required'
            })
        
        try:
            cart_total = Decimal(cart_total)
        except:
            cart_total = Decimal('0')
        
        is_valid, discount_amount, error = apply_coupon_to_order(coupon_code, cart_total)
        
        if is_valid:
            # Store coupon in session
            request.session['applied_coupon_code'] = coupon_code
            return JsonResponse({
                'success': True,
                'discount_amount': str(discount_amount),
                'message': f'Coupon "{coupon_code}" applied successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': error
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while applying coupon'
        })

@require_POST
def remove_coupon_view(request):
    """Remove applied coupon from cart"""
    try:
        if 'applied_coupon_code' in request.session:
            del request.session['applied_coupon_code']
        
        return JsonResponse({
            'success': True,
            'message': 'Coupon removed successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while removing coupon'
        })