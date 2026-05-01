import json
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .services import initiate_payment, verify_and_complete_payment, handle_payment_failure
from .models import Payment
from .serializers import PaymentSerializer


class InitiatePaymentView(APIView):
    """POST /api/payments/initiate/ → create Razorpay order"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response(
                {'error': 'order_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            data = initiate_payment(request.user, order_id)
            return Response(data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    """
    POST /api/payments/verify/ → called by frontend after user pays.
    The frontend receives payment details from Razorpay's JS modal
    and forwards them here for signature verification.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {'error': 'razorpay_order_id, razorpay_payment_id, and razorpay_signature are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            payment = verify_and_complete_payment(
                razorpay_order_id, razorpay_payment_id, razorpay_signature
            )
            return Response(PaymentSerializer(payment).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(APIView):
    """
    POST /api/payments/webhook/
    Receives events directly from Razorpay's servers.

    WHY @csrf_exempt?
    ──────────────────
    CSRF protection works by requiring a token that your browser sends
    with every form submission. Razorpay's servers don't have that token —
    they're not a browser. So we exempt this endpoint from CSRF.

    Instead, we verify the webhook signature for security.
    """
    permission_classes = [AllowAny]
    # AllowAny because this request comes from Razorpay, not your logged-in user

    def post(self, request):
        webhook_secret = settings.RAZORPAY_KEY_SECRET
        webhook_signature = request.headers.get('X-Razorpay-Signature', '')

        # Verify the webhook came from Razorpay
        try:
            razorpay.utility.Utility.verify_webhook_signature(
                request.body.decode('utf-8'),
                webhook_signature,
                webhook_secret
            )
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {'error': 'Invalid webhook signature'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payload = json.loads(request.body)
        event = payload.get('event')

        if event == 'payment.captured':
            # Payment captured = money is in your Razorpay account
            payment_data = payload['payload']['payment']['entity']
            razorpay_order_id = payment_data.get('order_id')
            razorpay_payment_id = payment_data.get('id')
            razorpay_signature = request.headers.get('X-Razorpay-Signature', '')

            try:
                verify_and_complete_payment(
                    razorpay_order_id, razorpay_payment_id, razorpay_signature
                )
            except ValueError:
                pass  # Already processed (idempotency) — silently ignore

        elif event == 'payment.failed':
            payment_data = payload['payload']['payment']['entity']
            razorpay_order_id = payment_data.get('order_id')
            failure_reason = payment_data.get('error_description', '')
            handle_payment_failure(razorpay_order_id, failure_reason)

        # Always return 200 to Razorpay — if you return 4xx/5xx,
        # Razorpay will keep retrying the webhook for hours.
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class PaymentStatusView(APIView):
    """GET /api/payments/order/<order_id>/ → check payment status"""
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            payment = Payment.objects.select_related('order').get(
                order__id=order_id,
                order__user=request.user
                # order__user = traverse FK → only return if order belongs to this user
            )
            return Response(PaymentSerializer(payment).data)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'No payment found for this order'},
                status=status.HTTP_404_NOT_FOUND
            )