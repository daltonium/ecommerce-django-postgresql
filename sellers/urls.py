from django.urls import path
from .views import SellerDashboardView, ProductAnalyticsView

urlpatterns = [
    path('seller/dashboard/', SellerDashboardView.as_view(), name='seller-dashboard'),
    path('seller/products/<int:product_id>/analytics/', ProductAnalyticsView.as_view(), name='product-analytics'),
]