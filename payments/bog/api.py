import uuid, requests, decimal
from django.conf import settings
from .client import get_token

ORDER_URL   = "https://api.bog.ge/payments/v1/ecommerce/orders"
DETAILS_URL = "https://api.bog.ge/payments/v1/receipt/{order_id}"

def create_order(amount_lari: int, basket: list[dict]) -> tuple[str, str]:
    """
    Returns (order_id, redirect_url) that your app passes to WebView.
    """
    payload = {
        "application_type": "mobile",
        "callback_url": settings.BOG["CALLBACK_URL"],
        "external_order_id": uuid.uuid4().hex,

        "purchase_units": {
            "currency": "GEL",
            "total_amount": amount_lari,      # integer!
            "basket": basket                   # optional but nice to have
        },
        "redirect_urls": {
            "success": settings.BOG["CALLBACK_URL"].replace("callback/", "success/"),
            "fail":    settings.BOG["CALLBACK_URL"].replace("callback/", "fail/"),
        },
    }
    print(f"this is my payload: {payload}")
    token = get_token()
    print(f"this is my token: {token}")

    r = requests.post(
        ORDER_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {token['access_token']}",
            "Content-Type": "application/json",
        },
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    return data["id"], data["_links"]["redirect"]["href"]


def fetch_details(order_id: str) -> dict:
    r = requests.get(
        DETAILS_URL.format(order_id=order_id),
        headers={"Authorization": f"Bearer {get_token()}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()
