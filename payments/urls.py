from django.urls import path
from . import views

urlpatterns = [
    # mobile-app APIs
    path("checkout/",          views.checkout,        name="payments-checkout"),
    path("status/<str:order_id>/", views.payment_status, name="payments-status"),
    path("my-videos/",         views.my_videos,       name="payments-my-videos"),

    # Bank callback
    path("bog/callback/", views.bog_callback, name="bog-callback"),

    # redirect URLs required by BoG
    path("success/", views.success, name="payment-success"),
    path("fail/",    views.fail,    name="payment-fail"),
]
