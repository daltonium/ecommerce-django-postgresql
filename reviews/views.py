from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer, ReplyCreateSerializer
from .services import create_review, add_reply
from products.permissions import IsSeller


class ProductReviewListView(APIView):
    """GET /api/products/<product_id>/reviews/ → public review list"""
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        reviews = Review.objects.filter(
            product_id=product_id
        ).select_related('user', 'reply', 'reply__seller')
        # Chain select_related through FK relationships:
        # 'reply' fetches the ReviewReply, 'reply__seller' fetches the seller User.
        # All in ONE JOIN query instead of N queries.

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class CreateReviewView(APIView):
    """POST /api/reviews/ → buyer submits a review"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            review = create_review(
                user=request.user,
                product_id=serializer.validated_data['product_id'],
                rating=serializer.validated_data['rating'],
                comment=serializer.validated_data.get('comment', '')
            )
            return Response(
                ReviewSerializer(review).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AddReplyView(APIView):
    """POST /api/reviews/reply/ → seller replies to a review"""
    permission_classes = [IsSeller]

    def post(self, request):
        serializer = ReplyCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            reply = add_reply(
                seller=request.user,
                review_id=serializer.validated_data['review_id'],
                content=serializer.validated_data['content']
            )
            from .serializers import ReviewReplySerializer
            return Response(ReviewReplySerializer(reply).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)