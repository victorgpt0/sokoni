from .models import Cart

def cart_context(request):
    """Add cart information to all templates"""
    cart = None
    cart_count = 0
    cart_total = 0
    
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(customer=request.user.customer).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, customer=None).first()
        
        if cart:
            cart_count = cart.total_items
            cart_total = cart.subtotal
    
    except (AttributeError, Cart.DoesNotExist):
        pass
    
    return {
        'cart': cart,
        'cart_count': cart_count,
        'cart_total': cart_total,
    }
