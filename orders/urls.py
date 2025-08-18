from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout process
    path('checkout/', views.checkout_view, name='checkout'),
    path('create/', views.create_order_view, name='create_order'),
    
    # Order management
    path('<str:order_number>/cancel/', views.cancel_order_view, name='cancel_order'),
    path('<str:order_number>/reorder/', views.reorder_view, name='reorder'),
    
    # Order tracking (public)
    path('track/<str:order_number>/', views.order_tracking_view, name='track_order'),
    path('<str:order_number>/invoice/', views.order_invoice_view, name='order_invoice'),
]
