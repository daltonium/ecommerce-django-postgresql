from django.urls import path
from .views import (
    CategoryListView, ProductListView, ProductDetailView,
    ProductCreateView, ProductImageUploadView, SellerProductListView
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),

    # Products — public
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # Products — seller only
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:product_id>/images/', ProductImageUploadView.as_view(), name='product-image-upload'),
    path('seller/products/', SellerProductListView.as_view(), name='seller-products'),
]