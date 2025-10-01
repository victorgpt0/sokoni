from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from products.models import Product

from .models import Wishlist


@login_required
def wishlist_list(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
        "product"
    )

    context = {
        "wishlist_items": wishlist_items,
    }
    return render(request, "wishlist/wishlist_list.html", context)


@login_required
def add_to_wishlist(request, product_id):
    """Add a product to user's wishlist"""
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        # Check if already in wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, product=product
        )

        if created:
            messages.success(request, f"{product.name} added to your wishlist!")
        else:
            messages.info(request, f"{product.name} is already in your wishlist!")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": "Product added to wishlist",
                    "in_wishlist": True,
                }
            )

        return redirect("wishlist:wishlist_list")

    return redirect("products:product_list")


@login_required
def remove_from_wishlist(request, product_id):
    """Remove a product from user's wishlist"""
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        try:
            wishlist_item = Wishlist.objects.get(user=request.user, product=product)
            wishlist_item.delete()
            messages.success(request, f"{product.name} removed from your wishlist!")
        except Wishlist.DoesNotExist:
            messages.error(request, "Product not found in wishlist!")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": "Product removed from wishlist",
                    "in_wishlist": False,
                }
            )

        return redirect("wishlist:wishlist_list")

    return redirect("wishlist:wishlist_list")


@login_required
def toggle_wishlist(request, product_id):
    """Toggle product in wishlist (add if not present, remove if present)"""
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        try:
            wishlist_item = Wishlist.objects.get(user=request.user, product=product)
            wishlist_item.delete()
            in_wishlist = False
            message = f"{product.name} removed from wishlist"
        except Wishlist.DoesNotExist:
            Wishlist.objects.create(user=request.user, product=product)
            in_wishlist = True
            message = f"{product.name} added to wishlist"

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": message, "in_wishlist": in_wishlist}
            )

        messages.success(request, message)
        next_url = request.META.get("HTTP_REFERER")
        if not url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            next_url = reverse("wishlist:wishlist_list")
        return redirect(next_url)

    return redirect("products:product_list")


@login_required
def wishlist_count(request):
    """Return wishlist count for AJAX requests"""
    count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({"count": count})
