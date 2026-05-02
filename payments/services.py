import razorpay
from django.conf import settings

from orders.models import Order
from .models import Payment


# WHY a module-level client variable named razorpay_client?
# The tests mock THIS exact name: patch('payments.services.razorpay_client')
# If you use a function like get_razorpay_client(), the tests can't patch it
# with a simple attribute mock — they'd need to patch the function return value.
# Module-level variable = single mock target, cleanest approach.
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def rupees_to_paise(amount):
    """
    Razorpay requires amounts in the smallest currency unit.
    Rs. 499.00 → 49900 paise.
    int() drops any floating-point noise after multiplication.
    """
    return int(amount * 100)


def initiate_payment(user, order_id):
    """
    Creates a Razorpay order for a given BlueCart order.

    WHY fetch order with user filter?
    If user A sends order_id belonging to user B, Order.DoesNotExist
    is raised → 404. This prevents users from initiating payments for
    other people's orders without leaking that the order exists.
    """
    try:
        order = Order.objects.get(id=order_id, user=user)
    except Order.DoesNotExist:
        raise ValueError("Order not found.")

    # WHY check status AFTER fetching?
    # If we did .get(id=..., status=PENDING, user=user) and the order is PAID,
    # Django raises DoesNotExist → view returns 404.
    # But 404 means "not found" — misleading. The order IS found, just wrong state.
    # Fetching first, then checking status returns the correct 400 semantic.
    if order.status != Order.Status.PENDING:
        raise ValueError("Order is not eligible for payment.")

    amount_in_paise = rupees_to_paise(order.total_amount)

    razorpay_order = razorpay_client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": 1,
        "notes": {
            "order_id": str(order.id),
            "user_id": str(user.id),
        },
    })

    # update_or_create = idempotent. If this endpoint is called twice
    # for the same order, we update the existing Payment instead of
    # creating a duplicate. Prevents IntegrityError on the OneToOne field.
    payment, _ = Payment.objects.update_or_create(
        order=order,
        defaults={
            "razorpay_order_id": razorpay_order["id"],
            "amount": order.total_amount,
            "status": Payment.Status.PENDING,
        }
    )

    return {
        "payment_id": payment.id,
        "order_id": order.id,
        "razorpay_order_id": razorpay_order["id"],
        "amount": amount_in_paise,
        "currency": "INR",
        "key": settings.RAZORPAY_KEY_ID,
    }


def verify_and_complete_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verifies Razorpay HMAC-SHA256 signature, then marks order PAID.

    WHY verify the signature?
    Anyone can POST to /api/payments/verify/. The signature proves
    the payload genuinely came from Razorpay — not a fake request
    trying to mark orders as paid for free.
    Raises razorpay.errors.SignatureVerificationError on tampered data.
    """
    razorpay_client.utility.verify_payment_signature({
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    })

    try:
        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
    except Payment.DoesNotExist:
        raise ValueError("Payment record not found.")

    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature  = razorpay_signature
    payment.status              = Payment.Status.COMPLETED
    payment.save()

    order = payment.order
    order.status = Order.Status.PAID
    order.save()

    return payment


def mark_payment_captured_from_webhook(razorpay_order_id, razorpay_payment_id):
    """
    Used by the webhook handler for payment.captured events.
    Idempotent — if already COMPLETED, does nothing and returns early.
    """
    payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()
    if not payment:
        return None

    if payment.status == Payment.Status.COMPLETED:
        return payment

    payment.razorpay_payment_id = razorpay_payment_id
    payment.status              = Payment.Status.COMPLETED
    payment.save()

    order = payment.order
    order.status = Order.Status.PAID
    order.save()

    return payment


def handle_payment_failure(razorpay_order_id, failure_reason=""):
    """
    Records a payment failure from the payment.failed webhook event.
    Silently does nothing if the Payment record doesn't exist.

    WHY no exception here?
    Payment failures are normal business events, not code errors.
    The webhook view always returns 200 to Razorpay — returning 4xx/5xx
    would cause Razorpay to retry the webhook for hours.
    """
    payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()
    if not payment:
        return None

    payment.status         = Payment.Status.FAILED
    payment.failure_reason = failure_reason
    payment.save()
    return payment
