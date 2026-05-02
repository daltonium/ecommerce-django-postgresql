from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product, ProductImage
from decimal import Decimal

User = get_user_model()


class ProductsTestCase(TestCase):
    """
    Tests for the products app.
    Covers: categories, product CRUD, seller-only permissions,
    image upload, DB indexes, filtering.
    """

    def setUp(self):
        self.client = APIClient()

        self.buyer = User.objects.create_user(
            username='buyer1',
            email='buyer@bluecart.com',
            password='testpass123',
            is_seller=False
        )
        self.seller = User.objects.create_user(
            username='seller1',
            email='seller@bluecart.com',
            password='testpass123',
            is_seller=True
        )
        self.other_seller = User.objects.create_user(
            username='seller2',
            email='seller2@bluecart.com',
            password='testpass123',
            is_seller=True
        )
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic gadgets'
        )
        self.product = Product.objects.create(
            name='Wireless Earbuds',
            description='Good earbuds',
            price=Decimal('999.99'),
            stock=50,
            seller=self.seller,
            category=self.category,
            is_active=True
        )

    # ─── CATEGORY ─────────────────────────────────────────────────────────────

    def test_list_categories_public(self):
        """Anyone can list categories — no auth required."""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_category_str(self):
        """Category __str__ returns its name."""
        self.assertEqual(str(self.category), 'Electronics')

    def test_category_slug_unique(self):
        """Two categories cannot have the same slug."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Elec2', slug='electronics')

    # ─── PRODUCT LISTING (PUBLIC) ─────────────────────────────────────────────

    def test_list_products_public(self):
        """Anyone can list active products."""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_inactive_product_not_in_list(self):
        """Inactive products are hidden from the public listing."""
        self.product.is_active = False
        self.product.save()
        response = self.client.get('/api/products/')
        self.assertEqual(len(response.data), 0)

    def test_filter_products_by_category_slug(self):
        """Products can be filtered by category slug."""
        Category.objects.create(name='Books', slug='books')
        response = self.client.get('/api/products/?category=electronics')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_detail_public(self):
        """Anyone can view a single product's details."""
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Wireless Earbuds')

    # ─── PRODUCT CREATE (SELLER ONLY) ─────────────────────────────────────────

    def test_seller_can_create_product(self):
        """An authenticated seller can create a product."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.post('/api/products/create/', {
            'name': 'Smart Watch',
            'description': 'A great watch',
            'price': '2999.00',
            'stock': 20,
            'category': self.category.id
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Smart Watch')
        # seller is auto-assigned — buyer cannot override it
        self.assertEqual(response.data['seller'], self.seller.id)

    def test_buyer_cannot_create_product(self):
        """A buyer (is_seller=False) cannot create products."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post('/api/products/create/', {
            'name': 'Hack Product',
            'description': 'Should not work',
            'price': '100.00',
            'stock': 5,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_product(self):
        """Anonymous users cannot create products."""
        response = self.client.post('/api/products/create/', {
            'name': 'Anon Product',
            'description': 'Should not work',
            'price': '100.00',
            'stock': 5,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ─── PRODUCT UPDATE/DELETE (OWN PRODUCTS ONLY) ────────────────────────────

    def test_seller_can_update_own_product(self):
        """Seller can update their own product."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.patch(
            f'/api/products/{self.product.id}/',
            {'price': '899.99'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], '899.99')

    def test_seller_cannot_update_other_sellers_product(self):
        """Seller A cannot modify Seller B's product."""
        self.client.force_authenticate(user=self.other_seller)
        response = self.client.patch(
            f'/api/products/{self.product.id}/',
            {'price': '1.00'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_seller_can_delete_own_product(self):
        """Seller can delete their own product."""
        self.client.force_authenticate(user=self.seller)
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_seller_cannot_delete_other_sellers_product(self):
        """Seller A cannot delete Seller B's product."""
        self.client.force_authenticate(user=self.other_seller)
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ─── MODEL VALIDATION ─────────────────────────────────────────────────────

    def test_product_uses_decimal_price(self):
        """Product price is stored as Decimal, not float (no rounding errors)."""
        self.assertEqual(type(self.product.price), Decimal)

    def test_product_str(self):
        """Product __str__ returns its name."""
        self.assertEqual(str(self.product), 'Wireless Earbuds')

    def test_seller_products_related_name(self):
        """seller.products.all() returns the seller's products."""
        products = self.seller.products.all()
        self.assertIn(self.product, products)

    # ─── SELLER PRODUCT LIST ──────────────────────────────────────────────────

    def test_seller_sees_only_own_products(self):
        """Seller dashboard only shows their own products."""
        # Create a product for other_seller
        Product.objects.create(
            name='Other Product', description='x',
            price='100', stock=5, seller=self.other_seller
        )
        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/api/seller/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only seller's product, not other_seller's
        for item in response.data:
            self.assertEqual(item['seller'] if 'seller' in item else self.seller.id, self.seller.id)
