from django.shortcuts import render
from django.db.models import Q, Avg, Count
from products.models import Product, Category
from django.contrib.auth.decorators import login_required

def home(request):
    """Home page view with featured products, categories, and search functionality."""
    
    # Featured products (products marked as featured or with high ratings)
    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).prefetch_related('images', 'reviews')[:8]
    
    # If not enough featured products, add some popular ones
    if featured_products.count() < 8:
        popular_products = Product.objects.filter(
            is_active=True
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-avg_rating', '-review_count')[:8 - featured_products.count()]
        
        featured_products = list(featured_products) + list(popular_products)
    
    # New arrivals (recently added products)
    new_arrivals = Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:6]
    
    # Best sellers (products with most reviews/orders)
    best_sellers = Product.objects.filter(
        is_active=True
    ).annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:6]
    
    # Categories with product counts
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).filter(product_count__gt=0)[:8]
    
    # Search suggestions (popular search terms)
    search_suggestions = [
        'Electronics', 'Fashion', 'Home & Garden', 'Sports', 
        'Books', 'Beauty', 'Automotive', 'Baby & Kids'
    ]
    
    # Special offers (products with compare_price)
    special_offers = Product.objects.filter(
        is_active=True,
        compare_price__isnull=False
    ).prefetch_related('images')[:4]
    
    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'categories': categories,
        'search_suggestions': search_suggestions,
        'special_offers': special_offers,
    }
    
    return render(request, 'home.html', context)

