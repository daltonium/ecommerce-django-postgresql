from django.urls import path
from .views import CartView, CartItemView, ClearCartView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/clear/', ClearCartView.as_view(), name='cart-clear'),
    path('cart/items/<int:product_id>/', CartItemView.as_view(), name='cart-item'),
]