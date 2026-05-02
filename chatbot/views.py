from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ChatInputSerializer, ChatMessageSerializer, ChatSessionSerializer
from .services import chat, get_or_create_session, clear_session
from .models import ChatSession


class ChatView(APIView):
    """
    POST /api/chatbot/  → send a message, get AI reply
    GET  /api/chatbot/  → load conversation history
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = get_or_create_session(request.user)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)

    def post(self, request):
        serializer = ChatInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = chat(
            user=request.user,
            user_message=serializer.validated_data['message']
        )

        return Response({
            'reply': result['reply'],
            'session_id': result['session_id']
        })


class ClearChatView(APIView):
    """DELETE /api/chatbot/clear/ → start a fresh conversation"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        clear_session(request.user)
        return Response({'message': 'Chat history cleared. Starting fresh!'})