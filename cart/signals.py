from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Cart, CartItem


@receiver(user_logged_in)
def handle_cart_merge_on_login(sender, user, request, **kwargs):
    """
    Merge anonymous cart with user cart when user logs in
    """
    if request and hasattr(request, "session"):
        # Store the session key before login for cart merging
        session_key = request.session.session_key

        # If there's an anonymous cart, merge it
        if session_key:
            try:
                anonymous_cart = Cart.objects.get(
                    session_key=session_key, customer=None
                )
                if anonymous_cart.cart_items.exists():
                    # Get or create user cart
                    user_cart, created = Cart.objects.get_or_create(
                        customer=user.customer, defaults={"session_key": None}
                    )

                    # Merge cart items
                    for item in anonymous_cart.cart_items.all():
                        user_item, created = CartItem.objects.get_or_create(
                            cart=user_cart,
                            product=item.product,
                            defaults={"quantity": item.quantity},
                        )

                        if not created:
                            # Add quantities if item already exists
                            from django.conf import settings

                            user_item.quantity = min(
                                user_item.quantity + item.quantity,
                                getattr(settings, "CART_ITEM_MAX_QUANTITY", 99),
                            )
                            user_item.save()

                    # Delete anonymous cart
                    anonymous_cart.delete()

            except Cart.DoesNotExist:
                pass
