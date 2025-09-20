from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    # Product listing and search
    path("", views.ProductListView.as_view(), name="product_list"),
    path("search/", views.ProductListView.as_view(), name="product_search"),
    # CRUD operations (must come before slug-based routes)
    path("create/", views.ProductCreateView.as_view(), name="product_create"),
    path("my-products/", views.my_products, name="my_products"),
    # API endpoints
    path("api/featured/", views.featured_products_view, name="featured_products_api"),
    path(
        "api/search-suggestions/",
        views.search_suggestions_view,
        name="search_suggestions_api",
    ),
    # Categories
    path(
        "category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    # Product-specific CRUD operations
    path("<slug:slug>/edit/", views.ProductUpdateView.as_view(), name="product_update"),
    path(
        "<slug:slug>/delete/", views.ProductDeleteView.as_view(), name="product_delete"
    ),
    path(
        "<slug:slug>/images/", views.product_manage_images, name="product_manage_images"
    ),
    # Reviews
    path("<slug:product_slug>/review/add/", views.add_review_view, name="add_review"),
    # Product detail (must be last to avoid catching other routes)
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
