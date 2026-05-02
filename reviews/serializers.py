from rest_framework import serializers
from .models import Review, ReviewReply


class ReviewReplySerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = ReviewReply
        fields = ['id', 'seller_name', 'content', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    reply = ReviewReplySerializer(read_only=True)
    # Nested serializer for the reply — read_only because replies
    # are created through a separate endpoint, not inline here.

    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = [
            'id', 'user_name', 'product', 'rating',
            'comment', 'reply', 'created_at'
        ]
        read_only_fields = ['user_name', 'created_at']


class ReviewCreateSerializer(serializers.Serializer):
    """Plain serializer — just validates input. Service does the work."""
    product_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, default='', allow_blank=True)


class ReplyCreateSerializer(serializers.Serializer):
    review_id = serializers.IntegerField()
    content = serializers.CharField()