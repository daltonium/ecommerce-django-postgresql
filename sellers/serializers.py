from rest_framework import serializers
from products.models import Product
from orders.models import Order


class SellerProductStatsSerializer(serializers.ModelSerializer):
    review_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.DecimalField(
        max_digits=3, decimal_places=2, read_only=True, allow_null=True
    )
    units_sold = serializers.IntegerField(read_only=True, allow_null=True)
    revenue = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'stock', 'is_active',
            'review_count', 'avg_rating', 'units_sold', 'revenue'
        ]


class SellerOrderSerializer(serializers.ModelSerializer):
    buyer_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'buyer_email', 'total_amount', 'status', 'created_at']