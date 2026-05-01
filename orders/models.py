from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from products.models import Product


class Order(TimeStampedModel):
    """
    WHY store total_amount on the Order instead of computing it?
    ─────────────────────────────────────────────────────────────
    Product prices CHANGE over time. If you compute total from current
    product prices, an order from 6 months ago would show the wrong amount.
    Storing it at checkout time = a permanent, accurate historical record.
    """

    class Status(models.TextChoices):
        """
        TextChoices = an enum-like class for CharField choices.
        WHY use it instead of plain tuples like (('P', 'Pending'),)?
        - Status.PENDING gives you the value 'PENDING' — self-documenting
        - Order.Status.choices gives DRF/admin the full list automatically
        - Avoids typos: Status.PENDIG would be a NameError, 'PENDIG' silently passes
        """
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
        FAILED = 'FAILED', 'Failed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
        # on_delete=PROTECT = prevents deleting a user who has orders.
        # WHY PROTECT and not CASCADE here?
        # Deleting a user should NOT delete their order history.
        # Order history is financial data — it must be preserved.
        # PROTECT raises an error if you try to delete a user with orders,
        # forcing you to handle it deliberately (anonymize instead of delete).
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Stored at checkout time — never changes even if product price changes

    shipping_address = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.email} — {self.status}"


class OrderItem(TimeStampedModel):
    """
    Each line in an order. Notice price_at_purchase — critical for history.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
        # on_delete=PROTECT: don't allow deleting a product that has been ordered.
        # The order history must remain valid. A seller can only deactivate (is_active=False),
        # not hard-delete a product that has order history.
    )

    quantity = models.PositiveIntegerField()

    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    """
    WHY price_at_purchase and not product.price?
    ─────────────────────────────────────────────
    This is called a PRICE SNAPSHOT. It captures what the user
    actually paid, frozen at the moment of purchase.
    product.price can change tomorrow. This field never changes.
    Every real e-commerce system does this — it's non-negotiable.
    """

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name} @ {self.price_at_purchase}"