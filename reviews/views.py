from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from .services import create_review, add_reply


class ProductReviewView(APIView):
    """
    GET  /api/products/<product_id>/reviews/ — List reviews (public, no auth needed)
    POST /api/products/<product_id>/reviews/ — Create a review (auth required)

    WHY one view class for both GET and POST?
    Django routes requests by URL first, then by HTTP method.
    If both GET and POST share the same URL path, they must live in
    the same view class. DRF dispatches to get() or post() automatically
    based on the HTTP method in the request.

    WHY permission_classes = [AllowAny]?
    Anyone can read reviews — no login needed.
    For POST, we manually check request.user.is_authenticated inside
    the post() method and return 401 if not logged in.
    This gives us fine-grained control: public reads, protected writes,
    all on the same URL.
    """
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        reviews = Review.objects.filter(
            product_id=product_id
        ).select_related('user', 'reply', 'reply__seller')
        # select_related pre-fetches related user and reply data in a
        # single SQL JOIN instead of N+1 separate queries.

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, product_id):
        # Manual auth check — AllowAny class lets unauthenticated
        # requests reach here, so we guard POST manually.
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = ReviewCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            review = create_review(
                user=request.user,
                product_id=product_id,
                rating=serializer.validated_data['rating'],
                comment=serializer.validated_data.get('comment', '')
            )
            return Response(
                ReviewSerializer(review).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            # create_review raises ValueError for:
            # - No completed order for this product
            # - Duplicate review
            # - Rating out of range (1-5)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AddReplyView(APIView):
    """
    POST /api/reviews/reply/
    Allows a seller to reply to a review on their product.
    Only the seller who owns the reviewed product can reply.
    """

    def post(self, request):
        review_id = request.data.get('review_id')
        content = request.data.get('content')

        if not review_id or not content:
            return Response(
                {'error': 'review_id and content are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reply = add_reply(request.user, review_id, content)
            return Response(
                {'id': reply.id, 'content': reply.content},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
