"""Request-body ceiling applied in config.asgi before Django reads the body."""

import asyncio
from unittest import TestCase

from config.request_limits import RequestBodyLimitMiddleware

LIMIT = 100


class DjangoLikeApp:
    """Reads the whole body before answering, like Django's ASGI handler."""

    def __init__(self):
        self.called = False
        self.body = b""

    async def __call__(self, scope, receive, send):
        self.called = True
        if scope["type"] == "http":
            while True:
                message = await receive()
                self.body += message.get("body", b"")
                if not message.get("more_body", False):
                    break
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})


def run(scope, chunks, max_size=LIMIT):
    app = DjangoLikeApp()
    middleware = RequestBodyLimitMiddleware(app, max_size=max_size)
    messages = [
        {"type": "http.request", "body": chunk, "more_body": i < len(chunks) - 1}
        for i, chunk in enumerate(chunks)
    ]
    sent = []

    async def receive():
        return messages.pop(0)

    async def send(message):
        sent.append(message)

    asyncio.run(middleware(scope, receive, send))
    return app, sent


def http_scope(content_length=None):
    headers = [(b"content-type", b"multipart/form-data; boundary=x")]
    if content_length is not None:
        headers.append((b"content-length", str(content_length).encode()))
    return {"type": "http", "method": "POST", "path": "/", "headers": headers}


class TestRequestBodyLimit(TestCase):
    def test_refuses_a_declared_length_over_the_limit_without_reading_it(self):
        app, sent = run(http_scope(LIMIT + 1), [b"x" * (LIMIT + 1)])

        assert not app.called
        assert sent[0]["status"] == 413

    def test_lets_a_body_at_the_limit_through(self):
        app, sent = run(http_scope(LIMIT), [b"x" * LIMIT])

        assert app.called
        assert app.body == b"x" * LIMIT
        assert sent[0]["status"] == 200

    def test_stops_a_chunked_body_once_it_crosses_the_limit(self):
        app, sent = run(http_scope(), [b"x" * 60, b"x" * 60, b"x" * 60])

        assert app.body == b"x" * 60  # The second chunk was never handed over.
        assert [m["status"] for m in sent if "status" in m] == [413]

    def test_stops_a_body_longer_than_its_declared_length(self):
        app, sent = run(http_scope(10), [b"x" * 60, b"x" * 60])

        assert sent[0]["status"] == 413

    def test_zero_disables_the_limit(self):
        app, sent = run(http_scope(LIMIT * 10), [b"x" * LIMIT * 10], max_size=0)

        assert sent[0]["status"] == 200

    def test_a_malformed_length_is_left_to_django(self):
        scope = http_scope()
        scope["headers"].append((b"content-length", b"abc"))
        app, sent = run(scope, [b"x"])

        assert app.called
        assert sent[0]["status"] == 200

    def test_other_scopes_pass_through(self):
        app = DjangoLikeApp()
        middleware = RequestBodyLimitMiddleware(app, max_size=LIMIT)
        sent = []

        async def send(message):
            sent.append(message)

        asyncio.run(middleware({"type": "lifespan"}, None, send))

        assert app.called
