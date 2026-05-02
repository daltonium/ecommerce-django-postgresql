from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import TimeStampedModel
from django.db import models

User = get_user_model()


class TimeStampedModelTestCase(TestCase):
    """
    Tests for the core app.
    Covers: abstract model inheritance, auto timestamps.
    We can't test TimeStampedModel directly (it's abstract),
    so we use a concrete model that inherits from it.
    """

    def setUp(self):
        """
        WHY test an abstract model indirectly?
        ────────────────────────────────────────
        Abstract models have no DB table — you can't create instances.
        We test them through a concrete child model (Product, Order, etc.)
        or create a temporary test model. Here we use User which doesn't
        inherit TimeStampedModel, so we use Product as our proxy.
        """
        from products.models import Product, Category
        self.seller = User.objects.create_user(
            username='testseller',
            email='testseller@bluecart.com',
            password='testpass123',
            is_seller=True
        )
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.product = Product.objects.create(
            name='Test Phone',
            description='A test phone',
            price='499.99',
            stock=10,
            seller=self.seller,
            category=self.category
        )

    def test_timestamped_model_has_created_at(self):
        """All models inheriting TimeStampedModel have created_at."""
        self.assertIsNotNone(self.product.created_at)

    def test_timestamped_model_has_updated_at(self):
        """All models inheriting TimeStampedModel have updated_at."""
        self.assertIsNotNone(self.product.updated_at)

    def test_created_at_does_not_change_on_update(self):
        """created_at is set once and never changes (auto_now_add)."""
        original_created = self.product.created_at
        self.product.name = 'Updated Phone'
        self.product.save()
        self.product.refresh_from_db()

        self.assertEqual(self.product.created_at, original_created)

    def test_updated_at_changes_on_save(self):
        """updated_at changes every time the model is saved (auto_now)."""
        import time
        original_updated = self.product.updated_at
        time.sleep(0.01)  # Ensure time difference
        self.product.name = 'Modified Phone'
        self.product.save()
        self.product.refresh_from_db()

        self.assertGreater(self.product.updated_at, original_updated)
