from .models import Review, ReviewReply
from orders.models import Order, OrderItem
from products.models import Product


def create_review(user, product_id, rating, comment=''):
    """
    Creates a review for a product. Enforces:
    1. User must have a PAID order containing this product (purchase gate)
    2. User cannot review the same product twice (duplicate gate)
    3. Rating must be between 1 and 5 (validation gate)

    WHY a purchase gate?
    Without it, anyone — including people who never bought the product —
    could leave reviews. This protects review integrity.

    WHY raise ValueError instead of returning None?
    The view catches ValueError and returns a 400 response with the
    error message. This keeps business logic in the service layer
    and HTTP logic in the view layer — clean separation of concerns.
    """

    # Gate 1: Rating validation
    # Must be checked before hitting the database.
    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5.")

    # Gate 2: Purchase gate — user must have a PAID order with this product
    has_purchased = OrderItem.objects.filter(
        order__user=user,
        order__status=Order.Status.PAID,
        product_id=product_id,
    ).exists()

    if not has_purchased:
        raise ValueError("You can only review products you have purchased.")

    # Gate 3: Duplicate gate — one review per product per user
    already_reviewed = Review.objects.filter(
        user=user,
        product_id=product_id
    ).exists()

    if already_reviewed:
        raise ValueError("You have already reviewed this product.")

    # All gates passed — create the review
    product = Product.objects.get(id=product_id)
    review = Review.objects.create(
        user=user,
        product=product,
        rating=rating,
        comment=comment,
    )
    return review


def add_reply(seller, review_id, content):
    """
    Allows a seller to reply to a review on their product.
    Only the seller who owns the reviewed product can reply.

    WHY check product ownership?
    Without this check, any seller could reply to any review —
    even reviews on products they don't own. That would be a
    data integrity and UX bug.
    """
    try:
        review = Review.objects.select_related('product').get(id=review_id)
    except Review.DoesNotExist:
        raise ValueError("Review not found.")

    if review.product.seller != seller:
        raise ValueError("You can only reply to reviews on your own products.")

    # Create or update the reply (one reply per review)
    reply, created = ReviewReply.objects.update_or_create(
        review=review,
        defaults={
            'seller': seller,
            'content': content,
        }
    )
    return reply
