from django.db import transaction
from .models import Review, ReviewReply
from orders.models import Order, OrderItem
from products.models import Product


def has_purchased_product(user, product_id):
    """
    Checks if a user has at least one PAID order containing this product.

    WHY .exists() and not .count() or .first()?
    ─────────────────────────────────────────────
    .exists() generates: SELECT 1 FROM ... WHERE ... LIMIT 1
    It stops as soon as it finds ONE match — fastest possible check.
    .count() counts ALL matches. .first() fetches the full row.
    For boolean checks, always use .exists().
    """
    return OrderItem.objects.filter(
        order__user=user,
        order__status=Order.Status.PAID,
        product_id=product_id
    ).exists()


@transaction.atomic
def create_review(user, product_id, rating, comment=''):
    """Create a review — only if user purchased and hasn't reviewed yet."""

    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        raise ValueError("Product not found.")

    if not has_purchased_product(user, product_id):
        raise ValueError("You can only review products you have purchased.")

    # unique_together on the model handles the duplicate check at DB level.
    # But we raise a friendly error before hitting the DB constraint.
    if Review.objects.filter(user=user, product=product).exists():
        raise ValueError("You have already reviewed this product.")

    review = Review.objects.create(
        user=user,
        product=product,
        rating=rating,
        comment=comment
    )
    return review


def add_reply(seller, review_id, content):
    """Add a seller reply to a review."""
    try:
        review = Review.objects.select_related('product__seller').get(id=review_id)
    except Review.DoesNotExist:
        raise ValueError("Review not found.")

    # Only the product's seller can reply
    if review.product.seller != seller:
        raise ValueError("You can only reply to reviews on your own products.")

    # Update if reply already exists, create if not
    reply, created = ReviewReply.objects.update_or_create(
        review=review,
        defaults={'seller': seller, 'content': content}
        # update_or_create: if a reply exists for this review → UPDATE it.
        # If not → CREATE it. 'defaults' = fields to set/update.
        # This is perfect for "edit your reply" functionality too.
    )
    return reply