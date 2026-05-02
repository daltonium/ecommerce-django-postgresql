from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from products.models import Product


class Conversation(TimeStampedModel):
    """
    A conversation is tied to a specific product inquiry.
    WHY include product? Context matters — "is this still available?"
    vs generic chat. Seller can reference the product easily.

    unique_together ensures one conversation per buyer-seller-product combo.
    No duplicate threads for the same inquiry.
    """
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_conversations'
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_conversations'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('buyer', 'seller', 'product')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.buyer.email} ↔ {self.seller.email} | {self.product}"


class Message(TimeStampedModel):
    """
    Individual message inside a conversation.
    Supports text + optional file attachment.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField(blank=True)
    file = models.FileField(
        upload_to='messages/',
        blank=True,
        null=True
    )
    is_read = models.BooleanField(default=False)
    # is_read = for unread message badge counts (Phase 11 frontend)

    class Meta:
        ordering = ['created_at']
        # Oldest first — chat reads top to bottom chronologically

    def __str__(self):
        return f"[{self.conversation.id}] {self.sender.email}: {self.content[:40]}"