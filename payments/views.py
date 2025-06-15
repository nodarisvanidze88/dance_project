import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import VideoContentSerializer
from django.utils.timezone import localtime
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from products.models import VideoContent
from .models import PaymentOrder
from .bog.api import create_order
from .serializers import PaymentOrderSerializer, CheckoutRequestSerializer

# --------------------------------------------------------------------------
# 1.  POST /payments/checkout/   { "video_ids": [1,2,3] }
# --------------------------------------------------------------------------
checkout_request_example = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["video_ids"],
    properties={
        "video_ids": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_INTEGER),
            description="IDs of VideoContent the user is purchasing",
            example=[1, 2, 3],
        )
    },
)
@swagger_auto_schema(
    method='post',
    operation_summary="Create BoG order and get redirect URL",
    request_body=checkout_request_example,
    responses={
        201: openapi.Response(
            description="BoG order created",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "order_id": openapi.Schema(type=openapi.TYPE_STRING),
                    "redirect_url": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                },
            ),
        ),
        400: "Bad Request",
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    ser = CheckoutRequestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    video_ids = ser.validated_data["video_ids"]

    # fetch and validate videos
    videos = list(
        VideoContent.objects.filter(id__in=video_ids, is_active=True)
    )
    if not videos:
        return Response({"error": "no active videos found"}, status=404)
    if len(videos) != len(video_ids):
        return Response({"error": "some video_ids invalid"}, status=400)

    # calculate amount (discount if set)  ->  tetri (int)
    amount_lari = sum(
        (v.discount_price or v.price) for v in videos
    )

    basket = [
        {
            "product_id": str(v.id),
            "quantity": 1,
            "unit_price": int(v.discount_price or v.price)
        }
        for v in videos
    ]

    order_id, redirect_url = create_order(amount_lari, basket)

    # store in DB
    po = PaymentOrder.objects.create(
        user=request.user,
        order_id=order_id,
        amount=amount_lari,
        status="created",
    )
    po.videos.set(videos)

    return Response({"order_id": order_id, "redirect_url": redirect_url}, status=201)


# --------------------------------------------------------------------------
# 2.  GET /payments/status/<order_id>/      (the app polls until paid)
# --------------------------------------------------------------------------
@api_view(["GET"])
@swagger_auto_schema(
    operation_summary="Check current BoG order status",
    manual_parameters=[
        openapi.Parameter("order_id", openapi.IN_PATH, description="Order ID", type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response(
            description="Payment status",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "order_id": openapi.Schema(type=openapi.TYPE_STRING),
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="paid"),
                },
            ),
        ),
        404: "Not found",
    },
)
def payment_status(request, order_id):
    po = PaymentOrder.objects.filter(order_id=order_id, user=request.user).first()
    if not po:
        return Response({"error": "not found"}, status=404)
    return Response({"order_id": po.order_id, "status": po.status})


# --------------------------------------------------------------------------
# 3.  GET /payments/my-videos/              (show everything the user owns)
# --------------------------------------------------------------------------
@api_view(["GET"])
@swagger_auto_schema(
    operation_summary="Get list of all paid VideoContent for this user",
    responses={200: VideoContentSerializer(many=True)},
)
def my_videos(request):
    paid_orders = PaymentOrder.objects.filter(user=request.user, status="paid")
    videos = VideoContent.objects.filter(payment_orders__in=paid_orders).distinct()
    from .serializers import VideoContentSerializer
    return Response(VideoContentSerializer(videos, many=True).data)


# --------------------------------------------------------------------------
# 4.  Bank of Georgia  →  POST /payments/bog/callback/
# --------------------------------------------------------------------------
@csrf_exempt
def bog_callback(request):
    try:
        payload = json.loads(request.body)
        order_id   = payload["body"]["order_id"]
        status_key = payload["body"]["order_status"]["key"]   # paid / failed …
    except Exception:
        return HttpResponseBadRequest()

    PaymentOrder.objects.filter(order_id=order_id).update(status=status_key)
    return HttpResponse("OK", status=200)


# --------------------------------------------------------------------------
# 5.  Front-channel redirect URLs that BoG requires
#     They just return plain text – no templates at all.
# --------------------------------------------------------------------------
@csrf_exempt
def success(request):
    return HttpResponse("Payment success – you can close this tab.", status=200)

@csrf_exempt
def fail(request):
    return HttpResponse("Payment failed or cancelled.", status=200)


class SoldVideoReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = []

        payment_orders = PaymentOrder.objects.filter(status="paid").prefetch_related('videos', 'user')

        for order in payment_orders:
            for video in order.videos.all():
                data.append({
                    "Video Title": video.title_ka,
                    "Sold At": localtime(order.created_at).strftime("%Y-%m-%d %H:%M"),
                    "Price (GEL)": f"{video.discount_price or video.price:.2f}",
                    "Buyer": order.user.email_or_phone,
                    "Course Name": video.course.name_ka if video.course else "",
                    "Course Author": video.course.author.name_ka if video.course and video.course.author else "",
                })

        return Response(data)