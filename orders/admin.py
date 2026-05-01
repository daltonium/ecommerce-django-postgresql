from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price_at_purchase', 'subtotal']
    # readonly_fields in admin = these are shown but cannot be edited.
    # Order history must NEVER be editable — financial data is immutable.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount', 'created_at']
    # total_amount is read-only in admin too — never let it be changed manually.