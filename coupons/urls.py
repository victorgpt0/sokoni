from django.urls import path

from . import views

app_name = "coupons"

urlpatterns = [
    # API endpoints
    path("api/validate/", views.validate_coupon_api, name="validate_coupon_api"),
    path("apply/", views.apply_coupon_view, name="apply_coupon"),
    path("remove/", views.remove_coupon_view, name="remove_coupon"),
    # Admin views
    path("admin/list/", views.coupon_list_view, name="coupon_list"),
    path("admin/<int:coupon_id>/stats/", views.coupon_stats_view, name="coupon_stats"),
]
