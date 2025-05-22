import functools, time, requests
from django.conf import settings

import base64

AUTH_URL = "https://oauth2.bog.ge/auth/realms/bog/protocol/openid-connect/token"

@functools.lru_cache()
def get_token() -> str:
    basic = f'{settings.BOG["CLIENT_ID"]}:{settings.BOG["CLIENT_SECRET"]}'
    basic_b64 = base64.b64encode(basic.encode()).decode()
    print(f"Bog token: {basic_b64}")
    resp = requests.post(
        AUTH_URL,
        data={
            "grant_type": "client_credentials",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Authorization": f"Basic {basic_b64}"}
    )
    resp.raise_for_status()

    token = resp.json()

    # Expire the cache 60 s before the real expiry so we always refresh in time
    # get_token.cache_clear()
    # get_token.cache_expiry_ts = time.time() + resp.json()["expires_in"] - 60
    return token
