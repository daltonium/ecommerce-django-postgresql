import json
import razorpay
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Payment
from .serializers import PaymentSerializer


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response(
                {"error": "order_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = services.initiate_payment(request.user, order_id)
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            msg = str(e)
            if 'not found' in msg.lower():
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {
                    "error": "razorpay_order_id, razorpay_payment_id, and razorpay_signature are required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = services.verify_and_complete_payment(
                razorpay_order_id,
                razorpay_payment_id,
                razorpay_signature,
            )
            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
        except ValueError as e:
            msg = str(e)
            if 'not found' in msg.lower():
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Invalid payment signature"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class RazorpayWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        webhook_secret = services.settings.RAZORPAY_KEY_SECRET
        webhook_signature = request.headers.get("X-Razorpay-Signature", "")

        try:
            services.razorpay_client.utility.verify_webhook_signature(
                request.body.decode("utf-8"),
                webhook_signature,
                webhook_secret,
            )
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Invalid webhook signature"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payload = json.loads(request.body)
        event = payload.get("event")

        if event == "payment.captured":
            payment_data = payload["payload"]["payment"]["entity"]
            services.mark_payment_captured_from_webhook(
                payment_data.get("order_id"),
                payment_data.get("id"),
            )

        elif event == "payment.failed":
            payment_data = payload["payload"]["payment"]["entity"]
            services.handle_payment_failure(
                payment_data.get("order_id"),
                payment_data.get("error_description", ""),
            )

        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            payment = Payment.objects.select_related("order").get(
                order__id=order_id,
                order__user=request.user
            )
            return Response(PaymentSerializer(payment).data)
        except Payment.DoesNotExist:
            return Response(
                {"error": "No payment found for this order"},
                status=status.HTTP_404_NOT_FOUND
            )