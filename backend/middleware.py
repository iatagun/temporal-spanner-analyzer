import os
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Shared with backend/routers/spanner.py's _read_upload_bounded (which
# streams-and-counts as a second line of defense for clients that omit or
# lie about Content-Length). Read independently here to avoid a
# main<->routers import cycle -- it's one os.getenv call, not worth
# threading through module wiring for.
MAX_BODY_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_EXEMPT_PATHS = {"/api/health"}
_MAX_TRACKED_IPS = 10_000


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """Rejects any request whose declared Content-Length exceeds
    MAX_BODY_BYTES, before the body is ever read into a Pydantic model.
    /api/upload has its own streaming size check for the multipart path;
    this covers the JSON-body endpoints (/api/spanner, /api/compare,
    /api/trends, ...), which previously had no size guard at all.
    """

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                too_large = int(content_length) > MAX_BODY_BYTES
            except ValueError:
                too_large = False
            if too_large:
                return JSONResponse(
                    {
                        "detail": f"Request body exceeds the {MAX_BODY_BYTES // (1024 * 1024)}MB limit"
                    },
                    status_code=413,
                )
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory sliding-window rate limiter, per client IP. Sized for a
    single-instance deployment (Render free tier) -- a multi-instance
    deployment behind a load balancer would need a shared store (Redis
    etc.) instead of process-local state.
    """

    def __init__(self, app, requests_per_minute: int = RATE_LIMIT_PER_MINUTE):
        super().__init__(app)
        self.limit = requests_per_minute
        self._hits: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if self.limit <= 0 or request.url.path in RATE_LIMIT_EXEMPT_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = self._hits[client_ip]
        while hits and now - hits[0] > RATE_LIMIT_WINDOW_SECONDS:
            hits.popleft()

        if len(hits) >= self.limit:
            return JSONResponse(
                {"detail": "Rate limit exceeded, please slow down"},
                status_code=429,
            )

        hits.append(now)
        if len(self._hits) > _MAX_TRACKED_IPS:
            self._hits = defaultdict(deque, {ip: h for ip, h in self._hits.items() if h})
        return await call_next(request)
