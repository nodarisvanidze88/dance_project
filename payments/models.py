from accounts.models import CustomUser
from django.db import models
from products.models import VideoContent            # your existing app

class PaymentOrder(models.Model):
    """
    Stores the BoG order_id plus user & videos.
    """
    user     = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name="payment_orders"
    )
    videos   = models.ManyToManyField(VideoContent, related_name="payment_orders")

    order_id = models.CharField(max_length=60, unique=True)
    amount   = models.PositiveIntegerField()             # tetri (integer)
    status   = models.CharField(max_length=30, default="created")  # created/paid/failed…

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} – {self.order_id} – {self.status}"
