from rest_framework import serializers
from products.models import Product, Category

class SellerProductSerializer(serializers.ModelSerializer):
    """
    WHY a separate serializer from the buyer-facing ProductSerializer?
    ───────────────────────────────────────────────────────────────────
    Buyers see: name, price, image, rating (read-only).
    Sellers also need: stock, is_active, category write access.
    Mixing these into one serializer creates a mess of read_only exceptions.
    Separate serializers = clean intent per audience.
    """
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )
    # Write category by ID, read back the name string
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price',
            'stock', 'is_active', 'image',
            'category', 'category_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # Inject the seller from the request — never trust client-sent seller ID
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)