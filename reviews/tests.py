from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product
from cart.services import add_to_cart
from orders.services import create_order
from orders.models import Order
from reviews.models import Review, ReviewReply
from reviews.services import create_review, add_reply
from decimal import Decimal

User = get_user_model()


class ReviewsTestCase(TestCase):
    """
    Tests for the reviews app.
    Covers: purchase-gated reviews, unique_together enforcement,
    rating range validation, seller replies, avg rating annotation.
    """

    def setUp(self):
        self.client = APIClient()
        self.buyer = User.objects.create_user(
            username='buyer1', email='buyer@bluecart.com',
            password='testpass123', is_seller=False
        )
        self.buyer2 = User.objects.create_user(
            username='buyer2', email='buyer2@bluecart.com',
            password='testpass123', is_seller=False
        )
        self.seller = User.objects.create_user(
            username='seller1', email='seller@bluecart.com',
            password='testpass123', is_seller=True
        )
        self.other_seller = User.objects.create_user(
            username='seller2', email='seller2@bluecart.com',
            password='testpass123', is_seller=True
        )
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.product = Product.objects.create(
            name='Headphones', description='Good headphones',
            price=Decimal('1500.00'), stock=20,
            seller=self.seller, category=self.category
        )

    def _make_purchase(self, user=None):
        """Helper: add item to cart, create order, and mark it PAID."""
        user = user or self.buyer
        add_to_cart(user, self.product.id, 1)
        order = create_order(user)
        order.status = Order.Status.PAID
        order.save()
        return order

    # ─── PURCHASE GATE ────────────────────────────────────────────────────────

    def test_buyer_who_purchased_can_review(self):
        """A buyer who has a PAID order for the product can review it."""
        self._make_purchase()
        review = create_review(self.buyer, self.product.id, rating=5, comment='Great!')
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.user, self.buyer)

    def test_buyer_without_purchase_cannot_review(self):
        """A buyer who hasn't bought the product cannot leave a review."""
        with self.assertRaises(ValueError) as ctx:
            create_review(self.buyer, self.product.id, rating=4)
        self.assertIn('purchased', str(ctx.exception).lower())

    def test_pending_order_does_not_allow_review(self):
        """A PENDING (not yet paid) order does not grant review rights."""
        add_to_cart(self.buyer, self.product.id, 1)
        create_order(self.buyer)
        # Order remains PENDING — not paid

        with self.assertRaises(ValueError) as ctx:
            create_review(self.buyer, self.product.id, rating=4)
        self.assertIn('purchased', str(ctx.exception).lower())

    # ─── DUPLICATE REVIEW PREVENTION ─────────────────────────────────────────

    def test_cannot_review_same_product_twice(self):
        """
        unique_together on (user, product) prevents duplicate reviews.
        Tests that the service raises ValueError before the DB constraint fires.
        """
        self._make_purchase()
        create_review(self.buyer, self.product.id, rating=5)

        with self.assertRaises(ValueError) as ctx:
            create_review(self.buyer, self.product.id, rating=3)
        self.assertIn('already reviewed', str(ctx.exception).lower())

    def test_different_buyers_can_review_same_product(self):
        """Two different buyers can each review the same product."""
        self._make_purchase(user=self.buyer)
        self._make_purchase(user=self.buyer2)

        r1 = create_review(self.buyer, self.product.id, rating=5)
        r2 = create_review(self.buyer2, self.product.id, rating=3)

        self.assertEqual(Review.objects.filter(product=self.product).count(), 2)

    # ─── RATING VALIDATION ────────────────────────────────────────────────────

    def test_rating_below_1_rejected(self):
        """Rating of 0 is invalid."""
        self._make_purchase()
        with self.assertRaises(Exception):
            create_review(self.buyer, self.product.id, rating=0)

    def test_rating_above_5_rejected(self):
        """Rating of 6 is invalid."""
        self._make_purchase()
        with self.assertRaises(Exception):
            create_review(self.buyer, self.product.id, rating=6)

    def test_valid_ratings_1_to_5(self):
        """All ratings from 1 to 5 are valid."""
        self._make_purchase(user=self.buyer)
        review = create_review(self.buyer, self.product.id, rating=1)
        self.assertEqual(review.rating, 1)

    # ─── SELLER REPLY ─────────────────────────────────────────────────────────

    def test_seller_can_reply_to_review_on_own_product(self):
        """The product's seller can reply to a review."""
        self._make_purchase()
        review = create_review(self.buyer, self.product.id, rating=5)
        reply = add_reply(self.seller, review.id, "Thank you for the review!")

        self.assertEqual(reply.content, "Thank you for the review!")
        self.assertEqual(reply.seller, self.seller)

    def test_other_seller_cannot_reply_to_review(self):
        """A seller cannot reply to reviews on another seller's product."""
        self._make_purchase()
        review = create_review(self.buyer, self.product.id, rating=5)

        with self.assertRaises(ValueError) as ctx:
            add_reply(self.other_seller, review.id, "Trying to hijack!")
        self.assertIn('own products', str(ctx.exception).lower())

    def test_seller_reply_updates_existing_reply(self):
        """
        Replying twice updates the reply (not creates a duplicate).
        Tests the update_or_create logic in add_reply().
        """
        self._make_purchase()
        review = create_review(self.buyer, self.product.id, rating=5)
        add_reply(self.seller, review.id, "First reply")
        add_reply(self.seller, review.id, "Updated reply")

        # Should still be ONE reply (not two)
        self.assertEqual(ReviewReply.objects.filter(review=review).count(), 1)
        review.reply.refresh_from_db()
        self.assertEqual(review.reply.content, "Updated reply")

    # ─── AVERAGE RATING ───────────────────────────────────────────────────────

    def test_product_average_rating(self):
        """
        Avg rating annotation is correct.
        Tests annotate(avg_rating=Avg('reviews__rating')).
        """
        from django.db.models import Avg
        self._make_purchase(user=self.buyer)
        self._make_purchase(user=self.buyer2)

        create_review(self.buyer, self.product.id, rating=4)
        create_review(self.buyer2, self.product.id, rating=2)

        from products.models import Product
        product = Product.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).get(id=self.product.id)

        self.assertEqual(product.avg_rating, 3.0)  # (4+2)/2 = 3

    def test_product_with_no_reviews_has_null_avg_rating(self):
        """Product with zero reviews has avg_rating of None."""
        from django.db.models import Avg
        product = Product.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).get(id=self.product.id)

        self.assertIsNone(product.avg_rating)

    # ─── API ENDPOINTS ────────────────────────────────────────────────────────

    def test_list_reviews_for_product_public(self):
        """Anyone can read product reviews."""
        self._make_purchase()
        create_review(self.buyer, self.product.id, rating=5, comment='Love it!')
        response = self.client.get(f'/api/products/{self.product.id}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_review_api(self):
        """POST /api/products/<id>/reviews/ creates a review."""
        self._make_purchase()
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(f'/api/products/{self.product.id}/reviews/', {
            'rating': 4,
            'comment': 'Pretty good'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_review_api_requires_auth(self):
        """Submitting a review requires authentication."""
        response = self.client.post(f'/api/products/{self.product.id}/reviews/', {
            'rating': 4,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
