from django.db import models
from django.conf import settings
from orders.models import Order


class Payment(models.Model):

    class Status(models.TextChoices):
        # WHY TextChoices?
        # TextChoices creates an enum where each member has a .value (the DB string)
        # and a .label (the human-readable name).
        # Payment.Status.PENDING      → stores 'PENDING' in DB
        # Payment.Status.PENDING.label → returns 'Pending'
        # This is why services.py can use Payment.Status.PENDING safely.
        PENDING   = 'PENDING',   'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED    = 'FAILED',    'Failed'

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    razorpay_order_id   = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature  = models.CharField(max_length=300, blank=True, null=True)
    amount              = models.DecimalField(max_digits=10, decimal_places=2)
    status              = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    failure_reason = models.TextField(blank=True, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.razorpay_order_id} — {self.status}"
