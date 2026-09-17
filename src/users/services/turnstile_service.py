import requests
from django.conf import settings


def verify_turnstile(token: str) -> bool:
    """Verify the Turnstile token with Cloudflare's API."""
    if not token:
        return False

    response = requests.post(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        data={
            "secret": settings.TURNSTILE_SECRET_KEY,
            "response": token,
        },
    )
    result = response.json()
    return result.get("success", False)
