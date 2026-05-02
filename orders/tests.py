from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product
from cart.services import add_to_cart
from orders.models import Order, OrderItem
from orders.services import create_order, cancel_order
from decimal import Decimal

User = get_user_model()


class OrdersTestCase(TestCase):
    """
    Tests for the orders app.
    Covers: checkout flow, atomic transactions, price snapshots,
    stock decrement, race condition protection, order cancellation.
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
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Keyboard', description='Mechanical keyboard',
            price=Decimal('2500.00'), stock=10,
            seller=self.seller, category=self.category
        )
        self.product2 = Product.objects.create(
            name='Monitor', description='4K monitor',
            price=Decimal('15000.00'), stock=5,
            seller=self.seller, category=self.category
        )

    def _add_items_and_checkout(self, user=None, product=None, quantity=2):
        """Helper: add items to cart and create order."""
        user = user or self.buyer
        product = product or self.product
        add_to_cart(user, product.id, quantity)
        return create_order(user, shipping_address='Chennai, TN')

    # ─── CHECKOUT FLOW ────────────────────────────────────────────────────────

    def test_create_order_from_cart(self):
        """Checkout creates an Order with correct OrderItems."""
        add_to_cart(self.buyer, self.product.id, 2)
        add_to_cart(self.buyer, self.product2.id, 1)
        order = create_order(self.buyer, shipping_address='Chennai, TN')

        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.user, self.buyer)

    def test_order_total_amount_is_correct(self):
        """Order total = sum of (price * quantity) for all items."""
        add_to_cart(self.buyer, self.product.id, 2)   # 2500 * 2 = 5000
        add_to_cart(self.buyer, self.product2.id, 1)  # 15000 * 1 = 15000
        order = create_order(self.buyer)

        expected_total = Decimal('5000.00') + Decimal('15000.00')
        self.assertEqual(order.total_amount, expected_total)

    def test_price_snapshot_is_stored(self):
        """
        OrderItem stores price_at_purchase — not a live reference to product.price.
        This verifies the price snapshot pattern works correctly.
        """
        add_to_cart(self.buyer, self.product.id, 1)
        order = create_order(self.buyer)

        order_item = order.items.first()
        self.assertEqual(order_item.price_at_purchase, Decimal('2500.00'))

        # Now change the product price
        self.product.price = Decimal('9999.00')
        self.product.save()

        # Order item price must NOT change — it's a snapshot
        order_item.refresh_from_db()
        self.assertEqual(order_item.price_at_purchase, Decimal('2500.00'))

    def test_stock_decremented_after_order(self):
        """
        Product stock decreases by the ordered quantity after checkout.
        Tests the F() expression decrement.
        """
        initial_stock = self.product.stock  # 10
        add_to_cart(self.buyer, self.product.id, 3)
        create_order(self.buyer)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 3)  # 7

    def test_cart_cleared_after_order(self):
        """Cart is emptied after successful checkout."""
        from cart.services import get_or_create_cart
        add_to_cart(self.buyer, self.product.id, 2)
        create_order(self.buyer)

        cart = get_or_create_cart(self.buyer)
        self.assertEqual(cart.items.count(), 0)

    def test_empty_cart_raises_error(self):
        """Checking out an empty cart raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            create_order(self.buyer)
        self.assertIn('empty', str(ctx.exception).lower())

    # ─── STOCK VALIDATION AT CHECKOUT ─────────────────────────────────────────

    def test_checkout_fails_if_stock_runs_out(self):
        """
        If stock drops to zero BETWEEN cart add and checkout,
        the order is rejected and cart is NOT cleared (atomic rollback).
        """
        from cart.services import get_or_create_cart
        add_to_cart(self.buyer, self.product.id, 3)

        # Simulate stock being sold out by another user
        self.product.stock = 0
        self.product.save()

        with self.assertRaises(ValueError) as ctx:
            create_order(self.buyer)

        self.assertIn('stock', str(ctx.exception).lower())

        # Cart must still have items — transaction rolled back
        cart = get_or_create_cart(self.buyer)
        self.assertEqual(cart.items.count(), 1)

    def test_checkout_fails_for_inactive_product(self):
        """Checking out with an inactive product raises ValueError."""
        add_to_cart(self.buyer, self.product.id, 1)
        self.product.is_active = False
        self.product.save()

        with self.assertRaises(ValueError) as ctx:
            create_order(self.buyer)
        self.assertIn('available', str(ctx.exception).lower())

    # ─── ORDER CANCELLATION ───────────────────────────────────────────────────

    def test_cancel_pending_order_restores_stock(self):
        """Cancelling a PENDING order restores product stock."""
        add_to_cart(self.buyer, self.product.id, 3)
        order = create_order(self.buyer)

        stock_after_order = self.product.stock  # Should be 10-3=7
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

        cancel_order(self.buyer, order.id)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)  # Restored to original

    def test_cancel_changes_status_to_cancelled(self):
        """Cancelled order has status CANCELLED."""
        add_to_cart(self.buyer, self.product.id, 1)
        order = create_order(self.buyer)
        cancelled = cancel_order(self.buyer, order.id)
        self.assertEqual(cancelled.status, Order.Status.CANCELLED)

    def test_cannot_cancel_paid_order(self):
        """Only PENDING orders can be cancelled."""
        add_to_cart(self.buyer, self.product.id, 1)
        order = create_order(self.buyer)
        order.status = Order.Status.PAID
        order.save()

        with self.assertRaises(ValueError) as ctx:
            cancel_order(self.buyer, order.id)
        self.assertIn('pending', str(ctx.exception).lower())

    def test_cannot_cancel_another_users_order(self):
        """User cannot cancel someone else's order."""
        other_buyer = User.objects.create_user(
            username='other', email='other@bluecart.com',
            password='testpass123'
        )
        add_to_cart(self.buyer, self.product.id, 1)
        order = create_order(self.buyer)

        with self.assertRaises(ValueError):
            cancel_order(other_buyer, order.id)

    # ─── API ENDPOINTS ────────────────────────────────────────────────────────

    def test_order_list_requires_auth(self):
        """Order list returns 401 for unauthenticated users."""
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_api(self):
        """POST /api/orders/create/ creates an order from the cart."""
        add_to_cart(self.buyer, self.product.id, 2)
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post('/api/orders/create/', {
            'shipping_address': 'Chennai, TN'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')

    def test_get_order_list_api(self):
        """GET /api/orders/ returns only the current user's orders."""
        add_to_cart(self.buyer, self.product.id, 1)
        create_order(self.buyer)

        self.client.force_authenticate(user=self.buyer)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_cannot_see_other_users_orders(self):
        """User A cannot access User B's order detail."""
        other_buyer = User.objects.create_user(
            username='other', email='other@bluecart.com',
            password='testpass123'
        )
        add_to_cart(self.buyer, self.product.id, 1)
        order = create_order(self.buyer)

        # other_buyer tries to access buyer's order
        self.client.force_authenticate(user=other_buyer)
        response = self.client.get(f'/api/orders/{order.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_str_representation(self):
        """Order __str__ includes order id, email and status."""
        add_to_cart(self.buyer, self.product.id, 1)
        order = create_order(self.buyer)
        self.assertIn(str(order.id), str(order))
        self.assertIn('PENDING', str(order))
