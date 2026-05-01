from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'status', 'method', 'created_at']
    list_filter = ['status', 'method']
    search_fields = ['razorpay_order_id', 'razorpay_payment_id', 'order__user__email']
    readonly_fields = [
        'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature',
        'amount', 'created_at'
    ]
    # All payment data is read-only in admin.
    # The only field that should ever be manually changed is 'status'
    # (e.g., manually marking a REFUNDED payment).