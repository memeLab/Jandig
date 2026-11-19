"""Refuse oversized request bodies before Django reads them.

Django's ASGI handler reads the whole body (spooling it to disk past
FILE_UPLOAD_MAX_MEMORY_SIZE) before any view or form runs, so the per-type
upload limits in core.upload_limits only apply once a large body has already
been received. Granian has no body-size option, so this wrapper refuses
requests whose Content-Length is over the ceiling, and stops reading chunked
bodies as soon as they cross it.
"""

TOO_LARGE_BODY = b"Request body too large."


class RequestBodyTooLarge(Exception):
    pass


class RequestBodyLimitMiddleware:
    def __init__(self, app, max_size):
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not self.max_size:
            return await self.app(scope, receive, send)

        content_length = dict(scope.get("headers", [])).get(b"content-length")
        if content_length is not None:
            try:
                too_large = int(content_length) > self.max_size
            except ValueError:
                too_large = False  # Let Django answer the malformed header.
            if too_large:
                return await self._refuse(send)

        received = 0

        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_size:
                    raise RequestBodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except RequestBodyTooLarge:
            # Django reads the whole body before it starts a response, so
            # nothing has been sent yet.
            await self._refuse(send)

    @staticmethod
    async def _refuse(send):
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (b"content-type", b"text/plain; charset=utf-8"),
                    (b"content-length", str(len(TOO_LARGE_BODY)).encode()),
                    (b"connection", b"close"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": TOO_LARGE_BODY})
