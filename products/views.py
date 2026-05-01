from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer, ProductSerializer,
    ProductListSerializer, ProductImageSerializer
)
from .permissions import IsSellerOrReadOnly, IsSeller


class CategoryListView(generics.ListCreateAPIView):
    """
    generics.ListCreateAPIView = handles GET (list) + POST (create) in one class.
    WHY use generics instead of APIView?
    ─────────────────────────────────────
    Generic views eliminate boilerplate. ListCreateAPIView already knows how
    to paginate, filter, serialize, and return responses. You just configure it.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        WHY override get_queryset() instead of setting queryset directly?
        ──────────────────────────────────────────────────────────────────
        A plain queryset = Product.objects.all() is evaluated ONCE at class load.
        get_queryset() runs on EVERY request, so it can read query params
        (like ?category=electronics) and filter dynamically.
        """
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'seller'
        ).prefetch_related('images')
        # select_related('category', 'seller') = JOINs these FK tables in ONE SQL query.
        # Without it: Django makes a separate DB query for every product's category. 
        # With 50 products = 101 queries (1 + 50 + 50). This is the "N+1 problem."
        # select_related = 1 query. Always use it when accessing FK fields.

        # prefetch_related('images') = fetches all related images in ONE extra query.
        # Used for reverse FK / M2M. Different from select_related (which uses JOIN).

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
            # category__slug = double underscore traverses the FK relationship.
            # Filter products WHERE category.slug = 'electronics'

        return queryset


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/products/:id/     → retrieve
    PUT /api/products/:id/     → full update
    PATCH /api/products/:id/   → partial update
    DELETE /api/products/:id/  → delete
    All handled by RetrieveUpdateDestroyAPIView.
    """
    queryset = Product.objects.select_related('category', 'seller').prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [IsSellerOrReadOnly]


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsSeller]
    # Only sellers can create products. The serializer.create() auto-assigns seller.


class ProductImageUploadView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsSeller]
    parser_classes = [MultiPartParser, FormParser]
    # MultiPartParser + FormParser = tells DRF to accept multipart/form-data
    # (the format used for file uploads). Without this, file uploads are rejected.

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id)

        # Security check: only the product's seller can upload images to it
        if product.seller != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only upload images to your own products.")

        serializer.save(product=product)


class SellerProductListView(generics.ListAPIView):
    """Returns only the logged-in seller's own products."""
    serializer_class = ProductListSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Product.objects.filter(
            seller=self.request.user
        ).select_related('category').prefetch_related('images')