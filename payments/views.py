from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import json
import requests
import hashlib
import hmac

from .models import Payment, PaymentAttempt
from orders.models import Order

def get_paystack_headers():
    """Get Paystack API headers"""
    return {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

@login_required
def process_payment_view(request, order_number):
    """Initialize payment process"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        customer=request.user.customer,
        status='pending'
    )
    
    # Check if payment already exists
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.total_amount,
            'currency': settings.CURRENCY_CODE,
            'payment_method': 'paystack',
            'status': 'pending'
        }
    )
    
    if payment.is_successful:
        messages.info(request, 'This order has already been paid for')
        return redirect('accounts:order_detail', order_number=order_number)
    
    # Initialize Paystack transaction
    paystack_data = {
        'email': request.user.email,
        'amount': int(order.total_amount * 100),  # Paystack expects amount in kobo
        'currency': 'KES',  # Paystack supports KES for Kenyan Shillings
        'reference': f'sokoni_{order.order_number}_{payment.id}',
        'callback_url': request.build_absolute_uri(reverse('payments:paystack_webhook')),
        'metadata': {
            'order_number': order.order_number,
            'customer_name': request.user.get_full_name() or request.user.username,
            'customer_phone': getattr(request.user.customer, 'phone_number', ''),
            'custom_fields': [
                {
                    'display_name': 'Order Number',
                    'variable_name': 'order_number',
                    'value': order.order_number
                }
            ]
        }
    }
    
    try:
        print(f"Paystack Data: {paystack_data}")  # Debug
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            headers=get_paystack_headers(),
            json=paystack_data
        )
        
        print(f"Paystack Response Status: {response.status_code}")  # Debug
        print(f"Paystack Response: {response.text}")  # Debug
        
        if response.status_code == 200:
            data = response.json()
            if data['status']:
                # Update payment with Paystack details
                payment.paystack_reference = paystack_data['reference']
                payment.paystack_access_code = data['data']['access_code']
                payment.status = 'processing'
                payment.save()
                
                # Store payment reference in session
                request.session['payment_reference'] = paystack_data['reference']
                
                context = {
                    'order': order,
                    'payment': payment,
                    'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
                    'paystack_reference': paystack_data['reference'],
                    'paystack_access_code': data['data']['access_code'],
                    'amount': int(order.total_amount * 100),
                    'email': request.user.email,
                }
                
                return render(request, 'payments/process_payment.html', context)
            else:
                error_msg = data.get('message', 'Payment initialization failed')
                messages.error(request, f'Payment initialization failed: {error_msg}')
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('message', 'Payment service unavailable')
            messages.error(request, f'Payment service error: {error_msg}')
            
    except requests.RequestException as e:
        messages.error(request, f'Payment service unavailable: {str(e)}')
    
    return redirect('orders:checkout')

@csrf_exempt
def verify_payment_view(request):
    """Verify payment with Paystack"""
    reference = request.GET.get('reference') or request.POST.get('reference')
    
    if not reference:
        messages.error(request, 'Invalid payment reference')
        return redirect('cart:cart_detail')
    
    try:
        # Verify with Paystack
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers=get_paystack_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] and data['data']['status'] == 'success':
                # Get payment record
                try:
                    payment = Payment.objects.get(paystack_reference=reference)
                    order = payment.order
                    
                    # Verify amount matches
                    paid_amount = data['data']['amount'] / 100  # Convert from kobo
                    if abs(paid_amount - float(payment.amount)) > 0.01:
                        messages.error(request, 'Payment amount mismatch')
                        return redirect('orders:checkout')
                    
                    # Update payment status
                    payment.status = 'completed'
                    payment.paystack_transaction_id = data['data']['id']
                    payment.gateway_response = data['data']
                    payment.paid_at = timezone.now()
                    payment.save()
                    
                    # Update order status
                    order.payment_status = 'paid'
                    order.status = 'processing'
                    order.save()
                    
                    # Clear session data
                    if 'payment_reference' in request.session:
                        del request.session['payment_reference']
                    if 'pending_order_id' in request.session:
                        del request.session['pending_order_id']
                    
                    messages.success(request, f'Payment successful! Order {order.order_number} confirmed.')
                    return redirect('payments:payment_success', order_number=order.order_number)
                    
                except Payment.DoesNotExist:
                    messages.error(request, 'Payment record not found')
            else:
                # Payment failed
                try:
                    payment = Payment.objects.get(paystack_reference=reference)
                    payment.status = 'failed'
                    payment.failure_reason = data['data'].get('gateway_response', 'Payment failed')
                    payment.failed_at = timezone.now()
                    payment.gateway_response = data['data']
                    payment.save()
                    
                    # Record payment attempt
                    PaymentAttempt.objects.create(
                        payment=payment,
                        paystack_reference=reference,
                        status='failed',
                        gateway_response=data['data']
                    )
                    
                    messages.error(request, f'Payment failed: {payment.failure_reason}')
                except Payment.DoesNotExist:
                    messages.error(request, 'Payment verification failed')
        else:
            messages.error(request, 'Payment verification failed')
            
    except requests.RequestException:
        messages.error(request, 'Payment verification service unavailable')
    
    return redirect('orders:checkout')

@csrf_exempt
@require_POST
def paystack_webhook_view(request):
    """Handle Paystack webhooks"""
    # Verify webhook signature
    paystack_signature = request.headers.get('X-Paystack-Signature')
    
    if not paystack_signature:
        return HttpResponse(status=400)
    
    # Verify signature
    body = request.body
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        body,
        hashlib.sha512
    ).hexdigest()
    
    if not hmac.compare_digest(paystack_signature, computed_signature):
        return HttpResponse(status=400)
    
    try:
        data = json.loads(body)
        event = data.get('event')
        
        if event == 'charge.success':
            # Handle successful payment
            reference = data['data']['reference']
            
            try:
                payment = Payment.objects.get(paystack_reference=reference)
                
                if payment.status != 'completed':
                    payment.status = 'completed'
                    payment.paystack_transaction_id = data['data']['id']
                    payment.gateway_response = data['data']
                    payment.paid_at = timezone.now()
                    payment.save()
                    
                    # Update order
                    order = payment.order
                    order.payment_status = 'paid'
                    order.status = 'processing'
                    order.save()
                    
            except Payment.DoesNotExist:
                pass
                
        elif event in ['charge.failed', 'charge.dispute.create']:
            # Handle failed payment
            reference = data['data']['reference']
            
            try:
                payment = Payment.objects.get(paystack_reference=reference)
                payment.status = 'failed'
                payment.failure_reason = data['data'].get('gateway_response', 'Payment failed')
                payment.failed_at = timezone.now()
                payment.gateway_response = data['data']
                payment.save()
                
                # Record payment attempt
                PaymentAttempt.objects.create(
                    payment=payment,
                    paystack_reference=reference,
                    status='failed',
                    gateway_response=data['data']
                )
                
            except Payment.DoesNotExist:
                pass
        
        return HttpResponse(status=200)
        
    except json.JSONDecodeError:
        return HttpResponse(status=400)

@login_required
def payment_success_view(request, order_number):
    """Payment success page"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        customer=request.user.customer
    )
    
    payment = get_object_or_404(Payment, order=order)
    
    context = {
        'order': order,
        'payment': payment,
    }
    
    return render(request, 'payments/payment_success.html', context)

@login_required
def payment_failed_view(request, order_number):
    """Payment failed page"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        customer=request.user.customer
    )
    
    payment = get_object_or_404(Payment, order=order)
    
    context = {
        'order': order,
        'payment': payment,
    }
    
    return render(request, 'payments/payment_failed.html', context)

@login_required
def retry_payment_view(request, order_number):
    """Retry failed payment"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        customer=request.user.customer
    )
    
    payment = get_object_or_404(Payment, order=order)
    
    if payment.is_successful:
        messages.info(request, 'This order has already been paid for')
        return redirect('accounts:order_detail', order_number=order_number)
    
    # Reset payment status for retry
    payment.status = 'pending'
    payment.save()
    
    return redirect('payments:process_payment', order_number=order_number)

@login_required
def test_paystack_view(request):
    """Test Paystack connectivity and keys"""
    try:
        # Test if keys are configured
        if not settings.PAYSTACK_PUBLIC_KEY or not settings.PAYSTACK_SECRET_KEY:
            return JsonResponse({
                'success': False,
                'error': 'Paystack keys not configured',
                'public_key': bool(settings.PAYSTACK_PUBLIC_KEY),
                'secret_key': bool(settings.PAYSTACK_SECRET_KEY)
            })
        
        # Test API connectivity
        response = requests.get(
            'https://api.paystack.co/transaction/totals',
            headers=get_paystack_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({
                'success': True,
                'message': 'Paystack connection successful',
                'data': data
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Paystack API error: {response.status_code}',
                'response': response.text
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Connection error: {str(e)}'
        })