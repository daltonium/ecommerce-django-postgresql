from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from core.models import TimeStampedModel
from products.models import Product


class Review(TimeStampedModel):
    """
    Business rule: a buyer can only review a product they actually purchased,
    and only once. We enforce the "only once" rule with unique_together.
    The "must have purchased" rule is enforced in the service layer.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
        # validators run at serializer .is_valid() time — not at DB level.
        # They raise ValidationError automatically before save() is called.
        # PositiveSmallIntegerField = tiny DB column (1 byte) — perfect for 1-5 ratings.
    )

    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'product')
        # WHY unique_together here?
        # Prevents one user leaving 5 reviews for the same product to inflate ratings.
        # The DB enforces this with a UNIQUE constraint — no application logic needed.
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} → {self.product.name} ({self.rating}★)"


class ReviewReply(TimeStampedModel):
    """
    Seller's reply to a review. One reply per review — OneToOneField.
    Only the product's seller can reply (enforced in the service).
    """
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='reply'
        # related_name='reply' → review.reply gives the reply directly.
        # If no reply exists, accessing review.reply raises ReviewReply.DoesNotExist.
        # Check with: hasattr(review, 'reply') before accessing.
    )

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_replies'
    )

    content = models.TextField()

    def __str__(self):
        return f"Reply to review #{self.review.id} by {self.seller.email}"