from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from .services import create_order, get_user_orders, cancel_order


class OrderCreateView(APIView):
    """POST /api/orders/ → checkout cart and create order"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = create_order(
                user=request.user,
                shipping_address=serializer.validated_data.get('shipping_address', '')
            )
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(APIView):
    """GET /api/orders/ → list all orders for the logged-in user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = get_user_orders(request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    """GET /api/orders/<id>/ → single order detail"""
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            # Filtering by BOTH id AND user ensures a user can't view someone else's order
            order = Order.objects.prefetch_related(
                'items', 'items__product'
            ).get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderCancelView(APIView):
    """POST /api/orders/<id>/cancel/ → cancel a pending order"""
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = cancel_order(request.user, order_id)
            return Response(OrderSerializer(order).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)