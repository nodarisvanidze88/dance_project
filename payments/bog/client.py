import functools, time, requests
from django.conf import settings

AUTH_URL = "https://oauth2.bog.ge/auth/realms/bog/protocol/openid-connect/token"

@functools.lru_cache()
def get_token() -> str:
    resp = requests.post(
        AUTH_URL,
        auth=(settings.BOG["CLIENT_ID"], settings.BOG["CLIENT_SECRET"]),
        data={"grant_type": "client_credentials"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    # expire 60 s early
    get_token.cache_clear()
    get_token.cache_token_expiry = time.time() + data["expires_in"] - 60
    return data["access_token"]
