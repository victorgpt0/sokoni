import json
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from coupons.models import Coupon
from products.models import Product

from .models import Cart, CartItem


def get_or_create_cart(request):
    """Get or create cart for authenticated user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            customer=request.user.customer, defaults={"session_key": None}
        )
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart, created = Cart.objects.get_or_create(
            session_key=session_key, customer=None
        )

    return cart


def cart_detail_view(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    cart_items = cart.cart_items.select_related("product").prefetch_related(
        "product__images"
    )

    # Calculate totals
    subtotal = cart.subtotal
    tax_amount = subtotal * settings.TAX_RATE

    # Check for free shipping
    shipping_cost = Decimal("0.00")
    if subtotal < settings.FREE_SHIPPING_THRESHOLD:
        shipping_cost = settings.DEFAULT_SHIPPING_COST

    total = subtotal + tax_amount + shipping_cost

    # Applied coupon (stored in session)
    applied_coupon = None
    discount_amount = Decimal("0.00")
    if "applied_coupon_code" in request.session:
        try:
            applied_coupon = Coupon.objects.get(
                code=request.session["applied_coupon_code"], is_active=True
            )
            if applied_coupon.is_valid and subtotal >= applied_coupon.minimum_amount:
                if applied_coupon.discount_type == "percentage":
                    discount_amount = subtotal * (applied_coupon.discount_value / 100)
                else:
                    discount_amount = applied_coupon.discount_value
                total -= discount_amount
        except Coupon.DoesNotExist:
            del request.session["applied_coupon_code"]

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "shipping_cost": shipping_cost,
        "discount_amount": discount_amount,
        "total": total,
        "applied_coupon": applied_coupon,
        "free_shipping_threshold": settings.FREE_SHIPPING_THRESHOLD,
        "free_shipping_remaining": max(0, settings.FREE_SHIPPING_THRESHOLD - subtotal),
    }

    return render(request, "cart/cart_detail.html", context)


@require_POST
def add_to_cart_view(request):
    """Add product to cart via AJAX"""
    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))

        if quantity <= 0 or quantity > settings.CART_ITEM_MAX_QUANTITY:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Quantity must be between 1 and {settings.CART_ITEM_MAX_QUANTITY}",
                }
            )

        product = get_object_or_404(Product, id=product_id, is_active=True)

        # Check stock
        if not product.is_in_stock:
            return JsonResponse({"success": False, "error": "Product is out of stock"})

        if quantity > product.stock_quantity:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Only {product.stock_quantity} items available",
                }
            )

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )

        if not created:
            # Update existing item
            new_quantity = cart_item.quantity + quantity
            if new_quantity > settings.CART_ITEM_MAX_QUANTITY:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Cannot add more than {settings.CART_ITEM_MAX_QUANTITY} of this item",
                    }
                )
            if new_quantity > product.stock_quantity:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Only {product.stock_quantity} items available",
                    }
                )
            cart_item.quantity = new_quantity
            cart_item.save()

        return JsonResponse(
            {
                "success": True,
                "message": f"{product.name} added to cart",
                "cart_count": cart.total_items,
                "cart_total": str(cart.subtotal),
            }
        )

    except Exception:
        return JsonResponse(
            {"success": False, "error": "An error occurred while adding to cart"}
        )


@require_POST
def update_cart_item_view(request):
    """Update cart item quantity via AJAX"""
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        quantity = int(data.get("quantity", 1))

        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            return remove_cart_item_view(request)

        if quantity > settings.CART_ITEM_MAX_QUANTITY:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Maximum quantity is {settings.CART_ITEM_MAX_QUANTITY}",
                }
            )

        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        # Check stock
        if quantity > cart_item.product.stock_quantity:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Only {cart_item.product.stock_quantity} items available",
                }
            )

        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Cart updated",
                "item_total": str(cart_item.total_price),
                "cart_subtotal": str(cart.subtotal),
                "cart_count": cart.total_items,
            }
        )

    except Exception:
        return JsonResponse(
            {"success": False, "error": "An error occurred while updating cart"}
        )


@require_POST
def remove_cart_item_view(request):
    """Remove item from cart via AJAX"""
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")

        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()

        return JsonResponse(
            {
                "success": True,
                "message": f"{product_name} removed from cart",
                "cart_subtotal": str(cart.subtotal),
                "cart_count": cart.total_items,
            }
        )

    except Exception:
        return JsonResponse(
            {"success": False, "error": "An error occurred while removing item"}
        )


@require_POST
def apply_coupon_view(request):
    """Apply coupon to cart"""
    coupon_code = request.POST.get("coupon_code", "").strip().upper()

    if not coupon_code:
        messages.error(request, "Please enter a coupon code")
        return redirect("cart:cart_detail")

    try:
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)

        if not coupon.is_valid:
            messages.error(request, "This coupon is not valid or has expired")
            return redirect("cart:cart_detail")

        cart = get_or_create_cart(request)
        subtotal = cart.subtotal

        if subtotal < coupon.minimum_amount:
            messages.error(
                request,
                f"Minimum order amount of ${coupon.minimum_amount} required for this coupon",
            )
            return redirect("cart:cart_detail")

        # Store coupon in session
        request.session["applied_coupon_code"] = coupon_code

        if coupon.discount_type == "percentage":
            discount = subtotal * (coupon.discount_value / 100)
            messages.success(
                request,
                f"Coupon applied! {coupon.discount_value}% discount (${discount:.2f})",
            )
        else:
            messages.success(
                request, f"Coupon applied! ${coupon.discount_value} discount"
            )

    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code")

    return redirect("cart:cart_detail")


def remove_coupon_view(request):
    """Remove applied coupon"""
    if "applied_coupon_code" in request.session:
        del request.session["applied_coupon_code"]
        messages.success(request, "Coupon removed")

    return redirect("cart:cart_detail")


def cart_mini_view(request):
    """Mini cart for AJAX updates"""
    cart = get_or_create_cart(request)
    cart_items = cart.cart_items.select_related("product").prefetch_related(
        "product__images"
    )[:5]

    context = {
        "cart": cart,
        "cart_items": cart_items,
    }

    return render(request, "cart/mini_cart.html", context)
