from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.permissions import IsSeller
from .services import get_seller_dashboard, get_product_analytics
from .serializers import SellerProductStatsSerializer, SellerOrderSerializer


class SellerDashboardView(APIView):
    """GET /api/seller/dashboard/ → full analytics"""
    permission_classes = [IsSeller]

    def get(self, request):
        data = get_seller_dashboard(request.user)

        return Response({
            'overall': {
                'total_revenue': data['overall']['total_revenue'] or 0,
                'total_orders': data['overall']['total_orders'] or 0,
                'total_units_sold': data['overall']['total_units_sold'] or 0,
            },
            'products': SellerProductStatsSerializer(
                data['products'], many=True
            ).data,
            'monthly_revenue': [
                {
                    'month': item['month'].strftime('%Y-%m'),
                    'revenue': str(item['revenue'])
                }
                for item in data['monthly_revenue']
            ],
            'recent_orders': SellerOrderSerializer(
                data['recent_orders'], many=True
            ).data,
        })


class ProductAnalyticsView(APIView):
    """GET /api/seller/products/<product_id>/analytics/"""
    permission_classes = [IsSeller]

    def get(self, request, product_id):
        try:
            data = get_product_analytics(request.user, product_id)
            return Response({
                'product_name': data['product'].name,
                'review_stats': data['review_stats']
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)