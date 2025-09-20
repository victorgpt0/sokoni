from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    # Payment processing
    path(
        "process/<str:order_number>/",
        views.process_payment_view,
        name="process_payment",
    ),
    path("verify/", views.verify_payment_view, name="verify_payment"),
    path("retry/<str:order_number>/", views.retry_payment_view, name="retry_payment"),
    # Payment status pages
    path(
        "success/<str:order_number>/",
        views.payment_success_view,
        name="payment_success",
    ),
    path(
        "failed/<str:order_number>/", views.payment_failed_view, name="payment_failed"
    ),
    # Webhooks
    path("webhook/paystack/", views.paystack_webhook_view, name="paystack_webhook"),
    # Debug/Test
    path("test/", views.test_paystack_view, name="test_paystack"),
]
