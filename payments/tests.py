from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from products.models import Category, Product
from cart.services import add_to_cart
from orders.services import create_order
from orders.models import Order
from decimal import Decimal

User = get_user_model()


class PaymentsTestCase(TestCase):
    """
    Tests for the payments app.
    Covers: Razorpay order creation, webhook signature verification,
    order status update, idempotent payment handling.

    WHY mock Razorpay?
    ─────────────────────────────────────────────────────────────
    We never call real external APIs in tests.
    Reasons:
      1. Tests would fail without internet access
      2. We'd need real API keys in the test environment
      3. Razorpay would charge for every test run
      4. Tests would be slow (network latency)
    Mock replaces razorpay.Client with a fake object we control.
    This tests OUR code, not Razorpay's servers.
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
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.product = Product.objects.create(
            name='Phone', description='Smartphone',
            price=Decimal('15000.00'), stock=10,
            seller=self.seller, category=self.category
        )
        add_to_cart(self.buyer, self.product.id, 1)
        self.order = create_order(self.buyer)

    # ─── PAYMENT ORDER CREATION ───────────────────────────────────────────────

    @patch('payments.services.razorpay_client')
    def test_create_payment_order(self, mock_razorpay):
        """
        POST /api/payments/create/ creates a Razorpay order.
        We mock razorpay_client.order.create() to return a fake response.
        """
        mock_razorpay.order.create.return_value = {
            'id': 'order_test123',
            'amount': 1500000,  # Razorpay uses paise (1 rupee = 100 paise)
            'currency': 'INR',
            'status': 'created'
        }

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post('/api/payments/create/', {
            'order_id': self.order.id
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('razorpay_order_id', response.data)
        self.assertEqual(response.data['razorpay_order_id'], 'order_test123')

        # Verify the amount sent to Razorpay was in paise
        call_dict = mock_razorpay.order.create.call_args[0][0]
        self.assertEqual(call_dict['amount'], 1500000)
        self.assertEqual(call_dict['currency'], 'INR')

    @patch('payments.services.razorpay_client')
    def test_cannot_create_payment_for_others_order(self, mock_razorpay):
        """User cannot initiate payment for another user's order."""
        other_buyer = User.objects.create_user(
            username='other', email='other@bluecart.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_buyer)
        response = self.client.post('/api/payments/create/', {
            'order_id': self.order.id
        }, format='json')
        self.assertIn(response.status_code, [
            status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND
        ])

    @patch('payments.services.razorpay_client')
    def test_cannot_pay_already_paid_order(self, mock_razorpay):
        """Cannot create payment for an already PAID order."""
        self.order.status = Order.Status.PAID
        self.order.save()

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post('/api/payments/create/', {
            'order_id': self.order.id
        }, format='json')
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT
        ])

    # ─── WEBHOOK VERIFICATION ─────────────────────────────────────────────────

    @patch('payments.services.razorpay_client')
    def test_valid_webhook_marks_order_paid(self, mock_razorpay):
        """
        POST /api/payments/verify/ with valid data marks order as PAID.
        We first seed a Payment row via /create/, then verify it.
        """
        mock_razorpay.order.create.return_value = {
            'id': 'order_rp_abc',
            'amount': 1500000,
            'currency': 'INR',
            'status': 'created',
        }
        mock_razorpay.utility.verify_payment_signature.return_value = None

        self.client.force_authenticate(user=self.buyer)

        # Step 1: seed the Payment row in the DB
        create_resp = self.client.post('/api/payments/create/', {
            'order_id': self.order.id
        }, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_200_OK)

        # Step 2: verify using the razorpay_order_id the mock returned
        response = self.client.post('/api/payments/verify/', {
            'razorpay_order_id':   'order_rp_abc',
            'razorpay_payment_id': 'pay_test456',
            'razorpay_signature':  'valid_signature',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PAID)
    @patch('payments.services.razorpay_client')
    def test_invalid_webhook_signature_rejected(self, mock_razorpay):
        """
        Webhook with tampered signature is rejected.
        Mock raises SignatureVerificationError.
        """
        import razorpay
        mock_razorpay.utility.verify_payment_signature.side_effect = (
            razorpay.errors.SignatureVerificationError('bad sig', 'verify')
        )

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post('/api/payments/verify/', {
            'razorpay_order_id': 'order_FAKE',
            'razorpay_payment_id': 'pay_FAKE',
            'razorpay_signature': 'TAMPERED',
            'order_id': self.order.id
        }, format='json')

        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN
        ])
        self.order.refresh_from_db()
        # Order should still be PENDING — not marked as paid
        self.assertEqual(self.order.status, Order.Status.PENDING)

    # ─── AMOUNT CONVERSION ────────────────────────────────────────────────────

    def test_amount_converted_to_paise(self):
        """
        Razorpay requires amounts in paise (smallest currency unit).
        ₹15000 must be sent as 1500000.
        """
        from payments.services import rupees_to_paise
        self.assertEqual(rupees_to_paise(Decimal('15000.00')), 1500000)
        self.assertEqual(rupees_to_paise(Decimal('100.50')), 10050)
        self.assertEqual(rupees_to_paise(Decimal('1.00')), 100)
