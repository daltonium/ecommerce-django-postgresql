import razorpay
import hmac
import hashlib
from django.conf import settings
from django.db import transaction
from .models import Payment
from orders.models import Order

# Initialize the Razorpay client once — reused across all calls
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def initiate_payment(user, order_id):
    """
    Step 1 of payment flow:
    - Verify the order belongs to the user and is PENDING
    - Create a Razorpay order (gives us a razorpay_order_id)
    - Store it in our Payment table
    - Return data the frontend needs to open the Razorpay payment modal
    """
    try:
        order = Order.objects.get(id=order_id, user=user, status=Order.Status.PENDING)
    except Order.DoesNotExist:
        raise ValueError("Order not found or not eligible for payment.")

    # Don't create a duplicate payment record if one already exists
    if hasattr(order, 'payment') and order.payment.status == Payment.Status.SUCCESS:
        raise ValueError("This order has already been paid.")

    # Convert rupees → paise (Razorpay requires paise)
    # WHY int()? Razorpay rejects floats. DecimalField * 100 gives Decimal, not int.
    amount_in_paise = int(order.total_amount * 100)

    # Call Razorpay API to create an order on their side
    razorpay_order = razorpay_client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"order_{order.id}",
        # receipt = your internal reference. Shown in Razorpay dashboard.
        "notes": {
            "bluecart_order_id": str(order.id),
            "user_email": user.email
        }
    })

    # Save the Razorpay order in our DB
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'razorpay_order_id': razorpay_order['id'],
            'amount': order.total_amount,
            'status': Payment.Status.CREATED,
        }
    )

    # Return everything the frontend Razorpay modal needs
    return {
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount_in_paise,
        'currency': 'INR',
        'order_id': order.id,
        'name': 'BlueCart',
        'email': user.email,
    }


def verify_and_complete_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Step 2 of payment flow — called after user completes payment.

    SIGNATURE VERIFICATION — critical security step:
    ─────────────────────────────────────────────────
    Razorpay signs its response using HMAC-SHA256 with your KEY_SECRET.
    We recompute the signature ourselves and compare.
    If they match: the response genuinely came from Razorpay.
    If they don't: someone forged the request. Reject it.

    Without this check, a hacker could send a fake "payment successful"
    request to your webhook and get free products.
    """

    # Recompute the signature
    message = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, razorpay_signature):
        # compare_digest = constant-time comparison.
        # WHY not == ?  Regular == short-circuits on first mismatch.
        # A timing attack could exploit this to guess the signature byte by byte.
        # compare_digest always takes the same time regardless of match length.
        raise ValueError("Invalid payment signature. Possible tampering detected.")

    # Fetch our Payment record
    try:
        payment = Payment.objects.select_related('order').get(
            razorpay_order_id=razorpay_order_id
        )
    except Payment.DoesNotExist:
        raise ValueError("Payment record not found.")

    # IDEMPOTENCY CHECK:
    # If this payment_id is already stored and status is SUCCESS,
    # return the existing record. Don't process it twice.
    if payment.status == Payment.Status.SUCCESS:
        return payment

    with transaction.atomic():
        # Fetch payment details from Razorpay to get the payment method
        payment_details = razorpay_client.payment.fetch(razorpay_payment_id)

        # Map Razorpay's method string to our Method enum
        method_map = {
            'upi': Payment.Method.UPI,
            'card': Payment.Method.CARD,
            'netbanking': Payment.Method.NETBANKING,
            'wallet': Payment.Method.WALLET,
        }
        method = method_map.get(
            payment_details.get('method', '').lower(),
            Payment.Method.UNKNOWN
        )

        # Update payment record
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = Payment.Status.SUCCESS
        payment.method = method
        payment.save()

        # Update the order status
        payment.order.status = Order.Status.PAID
        payment.order.save()

    return payment


def handle_payment_failure(razorpay_order_id, failure_reason=''):
    """Called when payment fails — update our records."""
    try:
        payment = Payment.objects.select_related('order').get(
            razorpay_order_id=razorpay_order_id
        )
    except Payment.DoesNotExist:
        return

    with transaction.atomic():
        payment.status = Payment.Status.FAILED
        payment.failure_reason = failure_reason
        payment.save()

        payment.order.status = Order.Status.FAILED
        payment.order.save()