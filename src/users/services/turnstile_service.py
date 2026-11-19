import logging

import requests
from django.conf import settings

log = logging.getLogger(__name__)

# Long enough for a slow answer, short enough that an outage at Cloudflare
# cannot hold a worker on every submission.
TURNSTILE_TIMEOUT_SECONDS = 5


def verify_turnstile(token: str) -> bool:
    """Verify the Turnstile token with Cloudflare's API.

    Fails closed: if Cloudflare cannot be reached or answers with something
    unreadable, the token counts as invalid rather than raising.
    """
    if not token:
        return False

    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": settings.TURNSTILE_SECRET_KEY,
                "response": token,
            },
            timeout=TURNSTILE_TIMEOUT_SECONDS,
        )
        result = response.json()
    except (requests.RequestException, ValueError):
        log.exception("Could not verify a Turnstile token")
        return False
    return isinstance(result, dict) and result.get("success") is True
