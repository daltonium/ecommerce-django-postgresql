from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from chatbot.models import ChatSession, ChatMessage
from chatbot.services import get_or_create_session, clear_session, build_chat_history

User = get_user_model()


class ChatbotTestCase(TestCase):
    """
    Tests for the chatbot app.
    Covers: session management, chat history building,
    Cohere API mocking, graceful error handling, clear session.

    WHY mock Cohere?
    ─────────────────────────────────────────────────────────────
    Same principle as mocking Razorpay:
      - No API key required in CI/test environment
      - No network calls = fast tests
      - We control the response to test OUR logic
      - Free tier has rate limits — tests would exhaust them
    We mock 'chatbot.services.co.chat' — the Cohere client method.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='user@bluecart.com',
            password='testpass123', is_seller=False
        )

    # ─── SESSION MANAGEMENT ───────────────────────────────────────────────────

    def test_session_created_on_first_chat(self):
        """A ChatSession is created when the user first interacts."""
        self.assertFalse(ChatSession.objects.filter(user=self.user).exists())
        get_or_create_session(self.user)
        self.assertTrue(ChatSession.objects.filter(user=self.user).exists())

    def test_one_active_session_per_user(self):
        """get_or_create_session never creates duplicate active sessions."""
        s1 = get_or_create_session(self.user)
        s2 = get_or_create_session(self.user)
        self.assertEqual(s1.id, s2.id)
        self.assertEqual(ChatSession.objects.filter(user=self.user, is_active=True).count(), 1)

    def test_clear_session_deactivates_current_session(self):
        """clear_session marks the active session as inactive."""
        session = get_or_create_session(self.user)
        self.assertTrue(session.is_active)

        clear_session(self.user)

        session.refresh_from_db()
        self.assertFalse(session.is_active)

    def test_new_session_created_after_clear(self):
        """After clearing, next get_or_create_session makes a fresh session."""
        old_session = get_or_create_session(self.user)
        clear_session(self.user)
        new_session = get_or_create_session(self.user)

        self.assertNotEqual(old_session.id, new_session.id)
        self.assertTrue(new_session.is_active)

    # ─── CHAT HISTORY BUILDING ────────────────────────────────────────────────

    def test_chat_history_format(self):
        """build_chat_history returns correct Cohere-formatted list."""
        session = get_or_create_session(self.user)
        ChatMessage.objects.create(
            session=session, role=ChatMessage.Role.USER, content='Hello'
        )
        ChatMessage.objects.create(
            session=session, role=ChatMessage.Role.CHATBOT, content='Hi there!'
        )

        history = build_chat_history(session)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['role'], 'USER')
        self.assertEqual(history[0]['message'], 'Hello')
        self.assertEqual(history[1]['role'], 'CHATBOT')
        self.assertEqual(history[1]['message'], 'Hi there!')

    def test_chat_history_limited_to_last_10(self):
        """
        Only the last 10 messages are sent to Cohere.
        Sending too many messages wastes tokens and slows responses.
        """
        session = get_or_create_session(self.user)
        for i in range(15):
            ChatMessage.objects.create(
                session=session,
                role=ChatMessage.Role.USER,
                content=f'Message {i}'
            )

        history = build_chat_history(session)
        self.assertEqual(len(history), 10)
        # Should be the LAST 10, not the first 10
        self.assertEqual(history[-1]['message'], 'Message 14')

    def test_empty_session_returns_empty_history(self):
        """New session returns empty history list."""
        session = get_or_create_session(self.user)
        history = build_chat_history(session)
        self.assertEqual(history, [])

    # ─── COHERE API CALL ──────────────────────────────────────────────────────

    @patch('chatbot.services.co')
    def test_chat_sends_message_and_saves_response(self, mock_co):
        """
        chat() calls Cohere API, saves user message AND AI response to DB.
        """
        mock_response = MagicMock()
        mock_response.text = 'Here are products under ₹500...'
        mock_co.chat.return_value = mock_response

        from chatbot.services import chat
        result = chat(self.user, 'Show me products under ₹500')

        self.assertEqual(result['reply'], 'Here are products under ₹500...')

        # Both user message and AI reply must be saved to DB
        session = get_or_create_session(self.user)
        messages = session.messages.all()
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].role, ChatMessage.Role.USER)
        self.assertEqual(messages[1].role, ChatMessage.Role.CHATBOT)

    @patch('chatbot.services.co')
    def test_cohere_api_failure_returns_fallback_message(self, mock_co):
        """
        If Cohere API raises an exception, the service returns a
        friendly fallback message — it does NOT crash the app.
        """
        mock_co.chat.side_effect = Exception("Connection timeout")

        from chatbot.services import chat
        result = chat(self.user, 'Hello')

        # Graceful fallback — not an exception
        self.assertIn('trouble', result['reply'].lower())

        # AI fallback message should still be saved to DB
        session = get_or_create_session(self.user)
        chatbot_messages = session.messages.filter(role=ChatMessage.Role.CHATBOT)
        self.assertEqual(chatbot_messages.count(), 1)

    @patch('chatbot.services.co')
    def test_cohere_called_with_correct_model(self, mock_co):
        """Cohere is called with the 'command-r' model."""
        mock_response = MagicMock()
        mock_response.text = 'Test reply'
        mock_co.chat.return_value = mock_response

        from chatbot.services import chat
        chat(self.user, 'Test')

        call_kwargs = mock_co.chat.call_args[1]
        self.assertEqual(call_kwargs.get('model'), 'command-r')

    # ─── API ENDPOINTS ────────────────────────────────────────────────────────

    def test_get_chat_history_api(self):
        """GET /api/chatbot/ returns the user's chat session."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/chatbot/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('messages', response.data)

    @patch('chatbot.services.co')
    def test_post_message_api(self, mock_co):
        """POST /api/chatbot/ sends a message and returns AI reply."""
        mock_response = MagicMock()
        mock_response.text = 'I can help you find products!'
        mock_co.chat.return_value = mock_response

        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/chatbot/', {
            'message': 'What products do you have?'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reply', response.data)
        self.assertEqual(response.data['reply'], 'I can help you find products!')

    def test_chatbot_api_requires_auth(self):
        """Unauthenticated users get 401."""
        response = self.client.post('/api/chatbot/', {'message': 'hello'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_message_rejected(self):
        """Empty message returns 400."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/chatbot/', {'message': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_message_over_500_chars_rejected(self):
        """
        Message over 500 characters is rejected.
        Tests the max_length=500 on ChatInputSerializer.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/chatbot/', {
            'message': 'A' * 501
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clear_chat_api(self):
        """DELETE /api/chatbot/clear/ deactivates the current session."""
        get_or_create_session(self.user)  # Ensure session exists
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/api/chatbot/clear/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ChatSession.objects.filter(user=self.user, is_active=True).exists())
