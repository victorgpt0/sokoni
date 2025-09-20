from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    # Cart views
    path("", views.cart_detail_view, name="cart_detail"),
    path("mini/", views.cart_mini_view, name="mini_cart"),
    # Cart actions (AJAX)
    path("add/", views.add_to_cart_view, name="add_to_cart"),
    path("update/", views.update_cart_item_view, name="update_cart_item"),
    path("remove/", views.remove_cart_item_view, name="remove_cart_item"),
    # Coupon actions
    path("coupon/apply/", views.apply_coupon_view, name="apply_coupon"),
    path("coupon/remove/", views.remove_coupon_view, name="remove_coupon"),
]
