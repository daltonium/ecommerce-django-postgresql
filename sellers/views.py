from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from products.models import Product
from .serializers import SellerProductSerializer
from .permissions import IsSeller

class SellerProductListView(APIView):
    """
    GET  /api/sellers/products/   → list only THIS seller's products
    POST /api/sellers/products/   → create a new product
    """
    permission_classes = [IsAuthenticated, IsSeller]

    def get(self, request):
        # filter by seller=request.user → sellers ONLY see their own products
        # Never use Product.objects.all() here — that's a data leak.
        products = Product.objects.filter(
            seller=request.user
        ).select_related('category').order_by('-created_at')
        serializer = SellerProductSerializer(
            products, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = SellerProductSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellerProductDetailView(APIView):
    """
    GET    /api/sellers/products/<id>/   → product detail
    PUT    /api/sellers/products/<id>/   → full update
    PATCH  /api/sellers/products/<id>/   → partial update (e.g. toggle is_active)
    DELETE /api/sellers/products/<id>/   → delete
    """
    permission_classes = [IsAuthenticated, IsSeller]

    def get_object(self, pk, user):
        """
        WHY filter by seller=user here and not just get(pk=pk)?
        ────────────────────────────────────────────────────────
        get(pk=pk) alone would let Seller A edit Seller B's product
        just by knowing the ID. Adding seller=user enforces ownership
        at the query level — the DB does the access check, not your code.
        """
        try:
            return Product.objects.get(pk=pk, seller=user)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response(
                {'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = SellerProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response(
                {'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = SellerProductSerializer(
            product, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response(
                {'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND
            )
        # partial=True → only the fields sent are updated; others untouched
        serializer = SellerProductSerializer(
            product, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response(
                {'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND
            )
        product.delete()
        return Response(
            {'message': 'Product deleted.'}, status=status.HTTP_204_NO_CONTENT
        )