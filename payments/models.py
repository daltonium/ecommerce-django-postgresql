from django.db import models
from core.models import TimeStampedModel
from orders.models import Order


class Payment(TimeStampedModel):

    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    class Method(models.TextChoices):
        UPI = 'UPI', 'UPI'
        CARD = 'CARD', 'Card'
        NETBANKING = 'NETBANKING', 'Net Banking'
        WALLET = 'WALLET', 'Wallet'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name='payment'
        # OneToOneField: one order has exactly one payment record.
        # on_delete=PROTECT: never delete an order that has payment data.
    )

    razorpay_order_id = models.CharField(max_length=100, unique=True)
    # This is the order ID Razorpay gives us when we initiate payment.
    # e.g., "order_PQR123abc". Unique because each order maps to one Razorpay order.

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
        # This is filled AFTER the user pays successfully.
        # e.g., "pay_XYZ789def"
        # unique=True = this payment ID can never appear twice → idempotency enforced at DB level.
    )

    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    # The cryptographic signature Razorpay sends with every payment.
    # We verify this to prove the request came from Razorpay, not a hacker.

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Stored in rupees. Razorpay works in paise (1 rupee = 100 paise).
    # We store in rupees and convert when calling Razorpay API.

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )

    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.UNKNOWN
    )

    failure_reason = models.TextField(blank=True)
    # Stores why a payment failed — useful for debugging and customer support.

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for Order #{self.order.id} — {self.status}"