from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import models

from products.models import Product
from products.serializers import ProductSerializer
from orders.models import Order
from .services import get_seller_dashboard, get_product_analytics
from .permissions import IsSeller


class SellerDashboardView(APIView):
    """
    GET /api/seller/dashboard/
    Returns revenue, order count, and top products for the logged-in seller.

    WHY IsSeller permission?
    We created a reusable permission class so every seller-only view
    declares permission_classes = [IsSeller] instead of repeating
    the is_seller check manually inside each method.
    DRF calls has_permission() before dispatch — view code never runs
    for non-sellers.
    """
    permission_classes = [IsSeller]

    def get(self, request):
        data = get_seller_dashboard(request.user)
        return Response(data)


class SellerProductListView(APIView):
    """
    GET /api/seller/products/
    Returns only products that belong to the logged-in seller.
    """
    permission_classes = [IsSeller]

    def get(self, request):
        products = Product.objects.filter(seller=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class SellerOrderListView(APIView):
    """
    GET /api/seller/orders/
    Returns orders containing at least one of the seller's products.

    WHY .distinct()?
    When filtering through a reverse FK (items__product__seller),
    an order with 2 items from the same seller would appear twice
    in results without .distinct(). We deduplicate with distinct().
    """
    permission_classes = [IsSeller]

    def get(self, request):
        orders = Order.objects.filter(
            items__product__seller=request.user
        ).distinct()

        data = [
            {
                'id': order.id,
                'status': order.status,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at,
            }
            for order in orders
        ]
        return Response(data)


class SellerOrderStatusView(APIView):
    """
    PATCH /api/seller/orders/<order_id>/status/
    Lets a seller mark an order as SHIPPED.

    WHY .filter().first() instead of .get()?
    The previous code used .get(id=order_id, items__product__seller=user)
    which crashed with MultipleObjectsReturned when an order had multiple
    items from the same seller — each item created a duplicate row in
    the JOIN before the filter was applied.

    .filter(...).first() avoids that entirely:
    - filter() returns a queryset (no crash on duplicates)
    - .distinct() deduplicates the JOIN rows
    - .first() safely picks the one matching order or returns None
    """
    permission_classes = [IsSeller]

    def patch(self, request, order_id):
        new_status = request.data.get('status')
        allowed_statuses = ['SHIPPED']

        if new_status not in allowed_statuses:
            return Response(
                {'error': f'Status must be one of: {allowed_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use filter().distinct().first() to avoid MultipleObjectsReturned
        # when the order has multiple items belonging to this seller.
        order = Order.objects.filter(
            id=order_id,
            items__product__seller=request.user
        ).distinct().first()

        if not order:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        order.status = new_status
        order.save()
        return Response({'status': order.status}, status=status.HTTP_200_OK)
