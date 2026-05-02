from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product
from cart.services import add_to_cart
from orders.services import create_order
from orders.models import Order
from decimal import Decimal

User = get_user_model()


class SellersTestCase(TestCase):
    """
    Tests for the sellers app.
    Covers: seller dashboard stats, annotate/aggregate queries,
    revenue calculation, buyer-cannot-access-seller-views.
    """

    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            username='seller1', email='seller@bluecart.com',
            password='testpass123', is_seller=True
        )
        self.other_seller = User.objects.create_user(
            username='seller2', email='seller2@bluecart.com',
            password='testpass123', is_seller=True
        )
        self.buyer = User.objects.create_user(
            username='buyer1', email='buyer@bluecart.com',
            password='testpass123', is_seller=False
        )
        self.category = Category.objects.create(name='Electronics', slug='electronics')

        self.product1 = Product.objects.create(
            name='Earbuds', description='Good earbuds',
            price=Decimal('999.00'), stock=50,
            seller=self.seller, category=self.category
        )
        self.product2 = Product.objects.create(
            name='Smartwatch', description='Smart watch',
            price=Decimal('3000.00'), stock=20,
            seller=self.seller, category=self.category
        )

        # Create paid orders for seller's products
        add_to_cart(self.buyer, self.product1.id, 2)
        add_to_cart(self.buyer, self.product2.id, 1)
        self.order = create_order(self.buyer)
        self.order.status = Order.Status.PAID
        self.order.save()

    # ─── DASHBOARD STATS ──────────────────────────────────────────────────────

    def test_seller_dashboard_accessible(self):
        """Seller can access their dashboard."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/seller/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_buyer_cannot_access_seller_dashboard(self):
        """Buyers (is_seller=False) are blocked from seller dashboard."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get('/api/seller/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_seller_dashboard(self):
        """Unauthenticated users get 401 on seller dashboard."""
        response = self.client.get('/api/seller/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_seller_total_revenue(self):
        """
        Seller dashboard returns correct total revenue from PAID orders.
        product1: 999 * 2 = 1998
        product2: 3000 * 1 = 3000
        Total = 4998
        """
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/seller/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(
            float(response.data['total_revenue']),
            4998.00,
            places=2
        )

    def test_seller_total_orders(self):
        """Dashboard shows correct count of PAID orders."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/seller/dashboard/')
        self.assertGreaterEqual(response.data['total_orders'], 1)

    def test_seller_sees_only_own_stats(self):
        """Seller dashboard only reflects their own products/orders."""
        # Create a product and order for the OTHER seller
        other_product = Product.objects.create(
            name='Other Item', description='Other item',
            price=Decimal('50000.00'), stock=5,
            seller=self.other_seller, category=self.category
        )
        other_buyer = User.objects.create_user(
            username='otherbuyer', email='otherbuyer@bluecart.com',
            password='testpass123'
        )
        add_to_cart(other_buyer, other_product.id, 1)
        other_order = create_order(other_buyer)
        other_order.status = Order.Status.PAID
        other_order.save()

        # Our seller's revenue must NOT include other_seller's 50000 sale
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/seller/dashboard/')
        self.assertAlmostEqual(
            float(response.data['total_revenue']),
            4998.00,
            places=2
        )

    def test_seller_top_products_in_dashboard(self):
        """Dashboard includes a top_products list."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/seller/dashboard/')
        self.assertIn('top_products', response.data)
        self.assertIsInstance(response.data['top_products'], list)

    # ─── SELLER PRODUCT MANAGEMENT ────────────────────────────────────────────

    def test_seller_product_list(self):
        """GET /api/seller/products/ returns only this seller's products."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/seller/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_seller_product_list_excludes_other_sellers(self):
        """Seller's product list does not include other sellers' products."""
        Product.objects.create(
            name='Other Seller Phone', description='x',
            price=Decimal('10000'), stock=3,
            seller=self.other_seller, category=self.category
        )
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/seller/products/')
        self.assertEqual(len(response.data), 2)  # Still just 2, not 3

    def test_seller_order_list(self):
        """GET /api/seller/orders/ returns orders containing seller's products."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/seller/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_seller_can_update_order_status(self):
        """Seller can mark an order as SHIPPED."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.patch(
            f'/api/seller/orders/{self.order.id}/status/',
            {'status': 'SHIPPED'},
            format='json'
        )
        self.assertIn(response.status_code, [
            status.HTTP_200_OK, status.HTTP_204_NO_CONTENT
        ])
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.SHIPPED)
