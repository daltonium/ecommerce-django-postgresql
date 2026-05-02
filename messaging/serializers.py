from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender_email', 'content', 'file', 'is_read', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    seller_email = serializers.EmailField(source='seller.email', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'buyer_email', 'seller_email', 'product_name',
            'last_message', 'unread_count', 'updated_at'
        ]

    def get_last_message(self, obj):
        last = obj.messages.last()
        return last.content[:60] if last else None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()