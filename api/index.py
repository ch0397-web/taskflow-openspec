import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mangum import Mangum
from backend.main import app as _fastapi_app


class StripPrefixMiddleware:
    """Strip /api prefix from path so FastAPI routes match on Vercel."""
    def __init__(self, app, prefix: str = "/api"):
        self.app = app
        self.prefix = prefix.encode()
        self.prefix_str = prefix

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path: str = scope.get("path", "")
            if path.startswith(self.prefix_str):
                scope["path"] = path[len(self.prefix_str):] or "/"
            raw: bytes = scope.get("raw_path", b"")
            if raw.startswith(self.prefix):
                scope["raw_path"] = raw[len(self.prefix):] or b"/"
        await self.app(scope, receive, send)


# Wrap FastAPI with prefix stripper, then wrap with Mangum for Vercel
app = StripPrefixMiddleware(_fastapi_app, "/api")
handler = Mangum(app, lifespan="auto")
