from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from products.models import Product


class ConversationListView(APIView):
    """GET /api/conversations/ → list all conversations for current user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(
            Q(buyer=request.user) | Q(seller=request.user)
        ).select_related(
            'buyer', 'seller', 'product'
        ).prefetch_related('messages')

        serializer = ConversationSerializer(
            conversations, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        """Start a new conversation about a product"""
        product_id = request.data.get('product_id')

        try:
            product = Product.objects.select_related('seller').get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if product.seller == request.user:
            return Response(
                {'error': 'You cannot message yourself about your own product'},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation, created = Conversation.objects.get_or_create(
            buyer=request.user,
            seller=product.seller,
            product=product
        )

        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class ConversationDetailView(APIView):
    """GET /api/conversations/<id>/ → full message history"""
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                Q(buyer=request.user) | Q(seller=request.user),
                id=conversation_id
            )
        except Conversation.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        # Mark all messages as read when conversation is opened
        Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        # .update() = one SQL UPDATE statement for ALL unread messages at once.
        # Never do this in a loop — each .save() in a loop = N queries.

        messages = conversation.messages.select_related('sender').all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)