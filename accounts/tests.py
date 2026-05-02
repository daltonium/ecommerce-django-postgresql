from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AccountsTestCase(TestCase):
    """
    Tests for the accounts app.
    Covers: registration, login, JWT tokens, /me/ endpoint, role handling.
    """

    def setUp(self):
        """
        setUp() runs before EVERY test method.
        WHY: Each test starts with a clean, known state.
        Django wraps each test in a transaction and rolls it back after —
        so data created in one test never bleeds into another.
        """
        self.client = APIClient()

        # Pre-create a user for tests that need an existing account
        self.existing_user = User.objects.create_user(
            username='existing',
            email='existing@bluecart.com',
            password='testpass123',
            is_seller=False
        )

        self.seller_user = User.objects.create_user(
            username='seller1',
            email='seller@bluecart.com',
            password='testpass123',
            is_seller=True
        )

    # ─── REGISTRATION ─────────────────────────────────────────────────────────

    def test_register_buyer_success(self):
        """A new buyer can register with valid data."""
        response = self.client.post('/api/auth/register/', {
            'username': 'newbuyer',
            'email': 'newbuyer@bluecart.com',
            'password': 'securepass123',
            'is_seller': False
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'newbuyer@bluecart.com')
        self.assertNotIn('password', response.data)
        # CRITICAL: password must NEVER appear in any response

    def test_register_seller_success(self):
        """A new seller can register with is_seller=True."""
        response = self.client.post('/api/auth/register/', {
            'username': 'newseller',
            'email': 'newseller@bluecart.com',
            'password': 'securepass123',
            'is_seller': True
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_seller'])

    def test_register_duplicate_email_fails(self):
        """Registering with an already-used email returns 400."""
        response = self.client.post('/api/auth/register/', {
            'username': 'duplicate',
            'email': 'existing@bluecart.com',  # already exists in setUp
            'password': 'securepass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password_fails(self):
        """Password under 8 characters is rejected."""
        response = self.client.post('/api/auth/register/', {
            'username': 'shortpass',
            'email': 'shortpass@bluecart.com',
            'password': '123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_email_fails(self):
        """Registration without email returns 400."""
        response = self.client.post('/api/auth/register/', {
            'username': 'noemail',
            'password': 'securepass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ─── LOGIN & JWT ──────────────────────────────────────────────────────────

    def test_login_success_returns_tokens(self):
        """Valid credentials return access and refresh tokens."""
        response = self.client.post('/api/auth/login/', {
            'email': 'existing@bluecart.com',
            'password': 'testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Tokens should be non-empty strings
        self.assertTrue(len(response.data['access']) > 50)
        self.assertTrue(len(response.data['refresh']) > 50)

    def test_login_wrong_password_fails(self):
        """Wrong password returns 401."""
        response = self.client.post('/api/auth/login/', {
            'email': 'existing@bluecart.com',
            'password': 'wrongpassword',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_email_fails(self):
        """Login with unregistered email returns 401."""
        response = self.client.post('/api/auth/login/', {
            'email': 'nobody@bluecart.com',
            'password': 'testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ─── /me/ ENDPOINT ────────────────────────────────────────────────────────

    def test_me_authenticated_returns_user_data(self):
        """Authenticated user gets their own profile."""
        self.client.force_authenticate(user=self.existing_user)
        # force_authenticate() bypasses JWT for testing — we test JWT separately
        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'existing@bluecart.com')
        self.assertNotIn('password', response.data)

    def test_me_unauthenticated_returns_401(self):
        """Unauthenticated request to /me/ returns 401."""
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_works(self):
        """A refresh token can be used to get a new access token."""
        # First login to get tokens
        login_response = self.client.post('/api/auth/login/', {
            'email': 'existing@bluecart.com',
            'password': 'testpass123',
        }, format='json')

        refresh_token = login_response.data['refresh']

        # Use refresh token to get a new access token
        refresh_response = self.client.post('/api/auth/token/refresh/', {
            'refresh': refresh_token
        }, format='json')

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    # ─── ROLE HANDLING ────────────────────────────────────────────────────────

    def test_buyer_is_not_seller_by_default(self):
        """Default registration creates a buyer (is_seller=False)."""
        response = self.client.post('/api/auth/register/', {
            'username': 'defaultbuyer',
            'email': 'defaultbuyer@bluecart.com',
            'password': 'securepass123',
        }, format='json')

        user = User.objects.get(email='defaultbuyer@bluecart.com')
        self.assertFalse(user.is_seller)

    def test_user_str_representation(self):
        """User __str__ returns email."""
        self.assertEqual(str(self.existing_user), 'existing@bluecart.com')
