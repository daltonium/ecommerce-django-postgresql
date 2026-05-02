from django.urls import path
from .views import (
    SellerDashboardView,
    SellerProductListView,
    SellerOrderListView,
    SellerOrderStatusView,
)

urlpatterns = [
    path('seller/dashboard/', SellerDashboardView.as_view(), name='seller-dashboard'),
    path('seller/products/', SellerProductListView.as_view(), name='seller-products'),
    path('seller/orders/', SellerOrderListView.as_view(), name='seller-orders'),
    path('seller/orders/<int:order_id>/status/', SellerOrderStatusView.as_view(), name='seller-order-status'),
]