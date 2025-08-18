from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Product, Category, ProductReview

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).prefetch_related('images', 'reviews')
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['price', '-price', 'name', '-name', '-created_at', 'created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', '-created_at')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related(
            'images', 'reviews__customer__user', 'category'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        
        # Reviews
        reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
        context['reviews'] = reviews[:5]  # Show first 5 reviews
        context['reviews_count'] = reviews.count()
        context['average_rating'] = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Rating distribution
        context['rating_distribution'] = {
            i: reviews.filter(rating=i).count() for i in range(1, 6)
        }
        
        return context

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get products in this category
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).prefetch_related('images', 'reviews')
        
        # Apply filters and sorting
        search_query = self.request.GET.get('search')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['price', '-price', 'name', '-name', '-created_at', 'created_at']:
            products = products.order_by(sort_by)
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get('page')
        context['products'] = paginator.get_page(page_number)
        
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = sort_by
        return context

def featured_products_view(request):
    """API endpoint for featured products"""
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).prefetch_related('images')[:8]
    
    products_data = []
    for product in featured_products:
        primary_image = product.images.filter(is_primary=True).first()
        products_data.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': str(product.price),
            'compare_price': str(product.compare_price) if product.compare_price else None,
            'image_url': primary_image.image.url if primary_image else None,
            'is_on_sale': product.is_on_sale,
            'discount_percentage': product.discount_percentage,
            'in_stock': product.is_in_stock,
        })
    
    return JsonResponse({'products': products_data})

def search_suggestions_view(request):
    """API endpoint for search suggestions"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Product suggestions
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True
    ).values('name', 'slug')[:5]
    
    # Category suggestions
    categories = Category.objects.filter(
        name__icontains=query,
        is_active=True
    ).values('name', 'slug')[:3]
    
    suggestions = {
        'products': list(products),
        'categories': list(categories)
    }
    
    return JsonResponse({'suggestions': suggestions})

def add_review_view(request, product_slug):
    """Add a product review"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    customer = request.user.customer
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return JsonResponse({'error': 'Valid rating (1-5) required'}, status=400)
        
        # Check if user already reviewed this product
        existing_review = ProductReview.objects.filter(
            product=product,
            customer=customer
        ).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.title = title
            existing_review.comment = comment
            existing_review.save()
            message = 'Review updated successfully'
        else:
            # Create new review
            ProductReview.objects.create(
                product=product,
                customer=customer,
                rating=rating,
                title=title,
                comment=comment
            )
            message = 'Review added successfully'
        
        return JsonResponse({'message': message})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)