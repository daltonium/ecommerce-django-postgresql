from django.urls import path
from .views import ProductReviewListView, CreateReviewView, AddReplyView

urlpatterns = [
    path('reviews/', CreateReviewView.as_view(), name='create-review'),
    path('reviews/reply/', AddReplyView.as_view(), name='add-reply'),
    path('products/<int:product_id>/reviews/', ProductReviewListView.as_view(), name='product-reviews'),
]