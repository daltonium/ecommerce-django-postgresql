from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class ChatSession(TimeStampedModel):
    """
    A chat session groups all messages for one user's conversation with the AI assistant. One user can have one active session.

    WHY store chat history in the DB?
    ──────────────────────────────────
    Cohere's API is stateless — it remembers nothing between calls.
    Every time you call it, you must send the conversation history yourself. 
    Storing it in DB = persistent memory across page refreshes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"ChatSession #{self.id} — {self.user.email}"


class ChatMessage(TimeStampedModel):
    """
    Individual message in a chat session.
    role = 'USER' or 'CHATBOT' — mirrors Cohere's message format exactly.
    """

    class Role(models.TextChoices):
        USER = 'USER', 'User'
        CHATBOT = 'CHATBOT', 'Chatbot'

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}"