from rest_framework import serializers
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    # many=True = this is a list (one product has many images)
    # read_only=True = images are returned in responses but not accepted in create/update.
    # We'll handle image upload separately via a dedicated endpoint.

    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    # source='category.name' = traverse the FK relationship and get the category's name.
    # WHY? Without this, the API returns category=3 (just an ID).
    # With it, it returns category_name="Electronics" — much more useful for the frontend.

    seller_name = serializers.CharField(
        source='seller.username',
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock',
            'category', 'category_name', 'seller', 'seller_name',
            'is_active', 'images', 'created_at'
        ]
        read_only_fields = ['seller', 'created_at']
        # seller is set automatically from request.user — not from the request body.

    def create(self, validated_data):
        # Automatically assign the logged-in user as the seller.
        # WHY here and not in the view? Keeps the view clean.
        # The view just calls serializer.save(), this method handles the logic.
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """
    A lighter serializer for list views.
    WHY two serializers?
    ────────────────────
    The full ProductSerializer returns all fields including images —
    expensive when listing 100 products. The list serializer returns
    only what the listing page needs. This is a common optimization.
    """
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'category_name', 'primary_image', 'is_active']

    def get_primary_image(self, obj):
        # SerializerMethodField = custom computed field.
        # get_<field_name>() is automatically called by DRF.
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            return request.build_absolute_uri(primary.image.url) if request else primary.image.url
            # build_absolute_uri converts '/media/products/img.jpg'
            # → 'http://localhost:8000/media/products/img.jpg'
            # The frontend needs the full URL, not a relative path.
        return None