from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product
from cart.models import Cart, CartItem
from cart.services import add_to_cart, update_cart_item, remove_from_cart, clear_cart, get_or_create_cart
from decimal import Decimal

User = get_user_model()


class CartTestCase(TestCase):
    """
    Tests for the cart app.
    Covers: cart creation, add/update/remove items,
    stock validation, duplicate merge, clear cart.
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
            name='Laptop', description='A laptop',
            price=Decimal('45000.00'), stock=10,
            seller=self.seller, category=self.category
        )
        self.product2 = Product.objects.create(
            name='Mouse', description='A mouse',
            price=Decimal('499.00'), stock=5,
            seller=self.seller, category=self.category
        )

    # ─── CART CREATION ────────────────────────────────────────────────────────

    def test_cart_auto_created_on_first_add(self):
        """A cart is automatically created when user first adds an item."""
        self.assertFalse(Cart.objects.filter(user=self.buyer).exists())
        add_to_cart(self.buyer, self.product.id, 1)
        self.assertTrue(Cart.objects.filter(user=self.buyer).exists())

    def test_one_cart_per_user(self):
        """get_or_create_cart never creates duplicate carts."""
        cart1 = get_or_create_cart(self.buyer)
        cart2 = get_or_create_cart(self.buyer)
        self.assertEqual(cart1.id, cart2.id)
        self.assertEqual(Cart.objects.filter(user=self.buyer).count(), 1)

    # ─── ADD TO CART ──────────────────────────────────────────────────────────

    def test_add_item_to_cart(self):
        """Adding a product creates a CartItem."""
        add_to_cart(self.buyer, self.product.id, 2)
        cart = get_or_create_cart(self.buyer)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_adding_same_product_merges_quantity(self):
        """
        Adding the same product twice merges into one CartItem.
        This tests the unique_together + get_or_create merge logic.
        """
        add_to_cart(self.buyer, self.product.id, 2)
        add_to_cart(self.buyer, self.product.id, 3)
        cart = get_or_create_cart(self.buyer)
        # Should still be ONE item, not two
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 5)

    def test_add_multiple_different_products(self):
        """Multiple different products create separate CartItems."""
        add_to_cart(self.buyer, self.product.id, 1)
        add_to_cart(self.buyer, self.product2.id, 2)
        cart = get_or_create_cart(self.buyer)
        self.assertEqual(cart.items.count(), 2)

    # ─── STOCK VALIDATION ─────────────────────────────────────────────────────

    def test_cannot_add_more_than_stock(self):
        """Adding quantity > stock raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            add_to_cart(self.buyer, self.product.id, 999)
        self.assertIn('available', str(ctx.exception).lower())

    def test_cannot_exceed_stock_on_merge(self):
        """Merging quantities that exceed stock raises ValueError."""
        add_to_cart(self.buyer, self.product.id, 8)
        # product has stock=10, already added 8
        with self.assertRaises(ValueError):
            add_to_cart(self.buyer, self.product.id, 5)  # 8+5=13 > 10

    def test_cannot_add_inactive_product(self):
        """Inactive products cannot be added to cart."""
        self.product.is_active = False
        self.product.save()
        with self.assertRaises(ValueError):
            add_to_cart(self.buyer, self.product.id, 1)

    def test_cannot_add_nonexistent_product(self):
        """Adding a non-existent product ID raises ValueError."""
        with self.assertRaises(ValueError):
            add_to_cart(self.buyer, 99999, 1)

    # ─── UPDATE CART ──────────────────────────────────────────────────────────

    def test_update_cart_item_quantity(self):
        """Updating a cart item changes its quantity."""
        add_to_cart(self.buyer, self.product.id, 2)
        update_cart_item(self.buyer, self.product.id, 5)
        cart = get_or_create_cart(self.buyer)
        self.assertEqual(cart.items.first().quantity, 5)

    def test_update_to_zero_removes_item(self):
        """Setting quantity to 0 removes the item from cart."""
        add_to_cart(self.buyer, self.product.id, 2)
        update_cart_item(self.buyer, self.product.id, 0)
        cart = get_or_create_cart(self.buyer)
        self.assertEqual(cart.items.count(), 0)

    def test_update_nonexistent_item_raises_error(self):
        """Updating an item not in cart raises ValueError."""
        with self.assertRaises(ValueError):
            update_cart_item(self.buyer, self.product.id, 3)

    # ─── REMOVE FROM CART ─────────────────────────────────────────────────────

    def test_remove_item_from_cart(self):
        """Removing an item deletes the CartItem."""
        add_to_cart(self.buyer, self.product.id, 2)
        remove_from_cart(self.buyer, self.product.id)
        cart = get_or_create_cart(self.buyer)
        self.assertEqual(cart.items.count(), 0)

    def test_remove_nonexistent_item_returns_false(self):
        """Removing an item not in cart returns False (no crash)."""
        result = remove_from_cart(self.buyer, self.product.id)
        self.assertFalse(result)

    # ─── CART TOTALS ──────────────────────────────────────────────────────────

    def test_cart_total_price(self):
        """cart.total_price correctly sums all item subtotals."""
        add_to_cart(self.buyer, self.product.id, 2)   # 45000 * 2 = 90000
        add_to_cart(self.buyer, self.product2.id, 3)  # 499 * 3 = 1497
        cart = get_or_create_cart(self.buyer)
        expected = Decimal('90000.00') + Decimal('1497.00')
        self.assertEqual(cart.total_price, expected)

    def test_cart_total_items(self):
        """cart.total_items returns total units across all items."""
        add_to_cart(self.buyer, self.product.id, 2)
        add_to_cart(self.buyer, self.product2.id, 3)
        cart = get_or_create_cart(self.buyer)
        self.assertEqual(cart.total_items, 5)

    # ─── API ENDPOINTS ────────────────────────────────────────────────────────

    def test_cart_api_requires_auth(self):
        """Cart API returns 401 for unauthenticated requests."""
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_cart_api(self):
        """GET /api/cart/ returns the user's cart."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertIn('total_price', response.data)

    def test_add_to_cart_api(self):
        """POST /api/cart/ adds an item and returns updated cart."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post('/api/cart/', {
            'product_id': self.product.id,
            'quantity': 2
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)

    def test_add_to_cart_api_missing_product_id(self):
        """POST /api/cart/ without product_id returns 400."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post('/api/cart/', {'quantity': 2}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clear_cart_api(self):
        """DELETE /api/cart/clear/ empties the cart."""
        add_to_cart(self.buyer, self.product.id, 2)
        self.client.force_authenticate(user=self.buyer)
        response = self.client.delete('/api/cart/clear/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart = get_or_create_cart(self.buyer)
        self.assertEqual(cart.items.count(), 0)
