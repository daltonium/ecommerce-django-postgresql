from rest_framework import serializers
from .models import ChatMessage, ChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']


class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=500,
        # Limit user input — prevent someone sending 10,000 words
        # which would burn through your Cohere token quota.
    )


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'messages', 'created_at']