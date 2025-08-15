from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product listing and search
    path('', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.ProductListView.as_view(), name='product_search'),
    
    # Categories
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Product detail
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # API endpoints
    path('api/featured/', views.featured_products_view, name='featured_products_api'),
    path('api/search-suggestions/', views.search_suggestions_view, name='search_suggestions_api'),
    
    # Reviews
    path('<slug:product_slug>/review/add/', views.add_review_view, name='add_review'),
]
