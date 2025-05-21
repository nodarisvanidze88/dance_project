import functools, time, requests
from django.conf import settings

import base64

AUTH_URL = "https://oauth2.bog.ge/auth/realms/bog/protocol/openid-connect/token"

@functools.lru_cache()
def get_token() -> str:
    authorization_basic = settings.BOG["CLIENT_ID"] + ":" + settings.BOG["CLIENT_SECRET"]
    # Check if the token is still valid
    base_64 = base64.b64encode(authorization_basic.encode()).decode()
    resp = requests.post(
        AUTH_URL,
        auth=f"Basic {base_64}",
        data={"grant_type": "client_credentials"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()
    data = resp.json()
    # expire 60 s early
    get_token.cache_clear()
    get_token.cache_token_expiry = time.time() + data["expires_in"] - 60
    return data["access_token"]
