# import functools, time, requests
# from django.conf import settings

# import base64

# AUTH_URL = "https://oauth2.bog.ge/auth/realms/bog/protocol/openid-connect/token"

# @functools.lru_cache()
# def get_token() -> str:
#     basic = f'{settings.BOG["CLIENT_ID"]}:{settings.BOG["CLIENT_SECRET"]}'
#     basic_b64 = base64.b64encode(basic.encode()).decode()
#     print(f"Bog token: {basic_b64}")
#     resp = requests.post(
#         AUTH_URL,
#         data={
#             "grant_type": "client_credentials",
#         },
#         headers={"Content-Type": "application/x-www-form-urlencoded",
#                  "Authorization": f"Basic {basic_b64}"}
#     )
#     resp.raise_for_status()

#     token = resp.json()

#     # Expire the cache 60 s before the real expiry so we always refresh in time
#     # get_token.cache_clear()
#     # get_token.cache_expiry_ts = time.time() + resp.json()["expires_in"] - 60
#     return token


# bog/client.py

import time
import base64
import requests
from django.conf import settings

AUTH_URL = "https://oauth2.bog.ge/auth/realms/bog/protocol/openid-connect/token"

_TOKEN: str | None = None
_TOKEN_EXPIRES_AT: float = 0.0  # unix timestamp


def get_token() -> str:
    """
    Return a valid BoG access token.

    Caches the token in memory and refreshes it a bit before expiry.
    """
    global _TOKEN, _TOKEN_EXPIRES_AT

    now = time.time()
    # refresh if no token yet or it's about to expire
    if _TOKEN is None or now >= _TOKEN_EXPIRES_AT:
        basic = f'{settings.BOG["CLIENT_ID"]}:{settings.BOG["CLIENT_SECRET"]}'
        basic_b64 = base64.b64encode(basic.encode()).decode()

        resp = requests.post(
            AUTH_URL,
            data={"grant_type": "client_credentials"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {basic_b64}",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        access_token = data["access_token"]
        expires_in = data.get("expires_in", 300)  # fallback 1h

        # Refresh 60 seconds before the real expiry
        _TOKEN = access_token
        _TOKEN_EXPIRES_AT = now + expires_in - 10

        print(f"BoG: fetched new token, expires_in={expires_in}s")

    return _TOKEN
