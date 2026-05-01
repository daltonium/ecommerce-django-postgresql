from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Cart
from .serializers import CartSerializer
from .services import add_to_cart, update_cart_item, remove_from_cart, clear_cart, get_or_create_cart


class CartView(APIView):
    """
    GET  /api/cart/   → view cart
    POST /api/cart/   → add item to cart
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_or_create_cart(request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            add_to_cart(request.user, product_id, quantity)
            # After adding, return the full updated cart
            cart = get_or_create_cart(request.user)
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError as e:
            # ValueError is raised by our service for stock issues, not found, etc.
            # We catch it here and return a clean 400 error — never expose raw exceptions.
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CartItemView(APIView):
    """
    PUT    /api/cart/items/<product_id>/  → update quantity
    DELETE /api/cart/items/<product_id>/  → remove item
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, product_id):
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {'error': 'quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            update_cart_item(request.user, product_id, int(quantity))
            cart = get_or_create_cart(request.user)
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        removed = remove_from_cart(request.user, product_id)
        if not removed:
            return Response(
                {'error': 'Item not in cart'},
                status=status.HTTP_404_NOT_FOUND
            )
        cart = get_or_create_cart(request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)


class ClearCartView(APIView):
    """DELETE /api/cart/clear/ → empty the entire cart"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        clear_cart(request.user)
        return Response({'message': 'Cart cleared.'}, status=status.HTTP_200_OK)