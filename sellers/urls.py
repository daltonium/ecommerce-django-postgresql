from django.urls import path
from .views import SellerProductListView, SellerProductDetailView

urlpatterns = [
    path('sellers/products/', SellerProductListView.as_view(), name='seller-products'),
    path('sellers/products/<int:pk>/', SellerProductDetailView.as_view(), name='seller-product-detail'),
]