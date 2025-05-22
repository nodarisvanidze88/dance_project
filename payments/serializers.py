from rest_framework import serializers
from products.models import VideoContent
from .models import PaymentOrder

class VideoContentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VideoContent
        fields = ["id", "title_ka", "title_en", "price", "discount_price"]

class PaymentOrderSerializer(serializers.ModelSerializer):
    videos = VideoContentSerializer(many=True, read_only=True)

    class Meta:
        model  = PaymentOrder
        fields = ["order_id", "status", "amount", "created_at", "videos"]

class CheckoutRequestSerializer(serializers.Serializer):
    video_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False
    )