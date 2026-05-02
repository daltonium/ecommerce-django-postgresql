from django.urls import path
from .views import AddReplyView, ProductReviewView

urlpatterns = [
    path("products/<int:product_id>/reviews/", ProductReviewView.as_view(), name="product-reviews"),
    path("reviews/reply/", AddReplyView.as_view(), name="review-reply"),
]