from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product
from messaging.models import Conversation, Message
from decimal import Decimal

User = get_user_model()


class MessagingTestCase(TestCase):
    """
    Tests for the messaging app.
    Covers: conversation creation, message history, unread counts,
    mark as read, access control (only participants can read),
    buyer-cannot-message-own-product.

    NOTE: WebSocket consumers are NOT tested here.
    Consumer tests require Django Channels test utilities (WebsocketCommunicator).
    The HTTP REST API (conversation list/detail) is fully tested below.
    """

    def setUp(self):
        self.client = APIClient()
        self.buyer = User.objects.create_user(
            username='buyer1', email='buyer@bluecart.com',
            password='testpass123', is_seller=False
        )
        self.seller = User.objects.create_user(
            username='seller1', email='seller@bluecart.com',
            password='testpass123', is_seller=True
        )
        self.outsider = User.objects.create_user(
            username='outsider', email='outsider@bluecart.com',
            password='testpass123', is_seller=False
        )
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.product = Product.objects.create(
            name='Laptop', description='Good laptop',
            price=Decimal('45000.00'), stock=5,
            seller=self.seller, category=self.category
        )

    # ─── CONVERSATION CREATION ────────────────────────────────────────────────

    def test_buyer_can_start_conversation_about_product(self):
        """POST /api/conversations/ creates a conversation for the product."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post('/api/conversations/', {
            'product_id': self.product.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Conversation.objects.filter(
            buyer=self.buyer, seller=self.seller, product=self.product
        ).exists())

    def test_starting_same_conversation_twice_returns_existing(self):
        """
        Starting a conversation for the same product again returns 200 (not 201).
        Tests unique_together + get_or_create idempotence.
        """
        self.client.force_authenticate(user=self.buyer)
        self.client.post('/api/conversations/', {'product_id': self.product.id}, format='json')
        response = self.client.post('/api/conversations/', {'product_id': self.product.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only ONE conversation should exist
        self.assertEqual(
            Conversation.objects.filter(buyer=self.buyer, seller=self.seller).count(), 1
        )

    def test_seller_cannot_message_own_product(self):
        """A seller cannot start a conversation about their own product."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.post('/api/conversations/', {
            'product_id': self.product.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_conversation_with_nonexistent_product_fails(self):
        """Starting a conversation for a non-existent product returns 404."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post('/api/conversations/', {
            'product_id': 99999
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ─── CONVERSATION LIST ────────────────────────────────────────────────────

    def test_user_sees_only_their_conversations(self):
        """
        GET /api/conversations/ returns only conversations the user is part of.
        """
        # Buyer starts a conversation
        Conversation.objects.create(buyer=self.buyer, seller=self.seller, product=self.product)

        # Outsider has no conversations
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get('/api/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_both_buyer_and_seller_see_conversation(self):
        """Both the buyer and seller can see the conversation in their list."""
        conv = Conversation.objects.create(
            buyer=self.buyer, seller=self.seller, product=self.product
        )

        self.client.force_authenticate(user=self.buyer)
        buyer_response = self.client.get('/api/conversations/')
        self.assertEqual(len(buyer_response.data), 1)

        self.client.force_authenticate(user=self.seller)
        seller_response = self.client.get('/api/conversations/')
        self.assertEqual(len(seller_response.data), 1)

    def test_conversation_list_requires_auth(self):
        """Unauthenticated request returns 401."""
        response = self.client.get('/api/conversations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ─── MESSAGE HISTORY ──────────────────────────────────────────────────────

    def test_get_conversation_message_history(self):
        """GET /api/conversations/<id>/ returns all messages."""
        conv = Conversation.objects.create(
            buyer=self.buyer, seller=self.seller, product=self.product
        )
        Message.objects.create(conversation=conv, sender=self.buyer, content='Is this available?')
        Message.objects.create(conversation=conv, sender=self.seller, content='Yes it is!')

        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(f'/api/conversations/{conv.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_outsider_cannot_read_conversation(self):
        """A user not in the conversation gets 404 on detail view."""
        conv = Conversation.objects.create(
            buyer=self.buyer, seller=self.seller, product=self.product
        )
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(f'/api/conversations/{conv.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ─── UNREAD MESSAGES ──────────────────────────────────────────────────────

    def test_messages_marked_as_read_when_conversation_opened(self):
        """
        Opening a conversation (GET detail) marks all unread messages as read.
        Tests the bulk .update(is_read=True) in ConversationDetailView.
        """
        conv = Conversation.objects.create(
            buyer=self.buyer, seller=self.seller, product=self.product
        )
        Message.objects.create(
            conversation=conv, sender=self.seller,
            content='Hi! Still available?', is_read=False
        )

        # Before opening: 1 unread message
        self.assertEqual(conv.messages.filter(is_read=False).count(), 1)

        # Buyer opens the conversation
        self.client.force_authenticate(user=self.buyer)
        self.client.get(f'/api/conversations/{conv.id}/')

        # After opening: 0 unread messages
        self.assertEqual(conv.messages.filter(is_read=False).count(), 0)

    def test_unread_count_in_conversation_list(self):
        """Conversation list includes unread_count for each conversation."""
        conv = Conversation.objects.create(
            buyer=self.buyer, seller=self.seller, product=self.product
        )
        Message.objects.create(
            conversation=conv, sender=self.seller,
            content='Message 1', is_read=False
        )
        Message.objects.create(
            conversation=conv, sender=self.seller,
            content='Message 2', is_read=False
        )

        self.client.force_authenticate(user=self.buyer)
        response = self.client.get('/api/conversations/')
        self.assertEqual(response.data[0]['unread_count'], 2)

    # ─── MODEL TESTS ──────────────────────────────────────────────────────────

    def test_conversation_str(self):
        """Conversation __str__ includes buyer and seller emails."""
        conv = Conversation.objects.create(
            buyer=self.buyer, seller=self.seller, product=self.product
        )
        self.assertIn('buyer@bluecart.com', str(conv))
        self.assertIn('seller@bluecart.com', str(conv))

    def test_message_ordering_is_chronological(self):
        """Messages are returned oldest-first."""
        conv = Conversation.objects.create(
            buyer=self.buyer, seller=self.seller, product=self.product
        )
        m1 = Message.objects.create(conversation=conv, sender=self.buyer, content='First')
        m2 = Message.objects.create(conversation=conv, sender=self.seller, content='Second')

        messages = list(conv.messages.all())
        self.assertEqual(messages[0].content, 'First')
        self.assertEqual(messages[1].content, 'Second')
