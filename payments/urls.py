from django.urls import path
from .views import (
    InitiatePaymentView,
    VerifyPaymentView,
    RazorpayWebhookView,
    PaymentStatusView,
)

urlpatterns = [
    path("payments/create/", InitiatePaymentView.as_view(), name="payment-create"),
    path("payments/verify/", VerifyPaymentView.as_view(), name="payment-verify"),
    path("payments/webhook/", RazorpayWebhookView.as_view(), name="payment-webhook"),
    path("payments/order/<int:order_id>/", PaymentStatusView.as_view(), name="payment-status"),
]