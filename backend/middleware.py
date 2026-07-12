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


def _too_large_response() -> JSONResponse:
    return JSONResponse(
        {"detail": f"Request body exceeds the {MAX_BODY_BYTES // (1024 * 1024)}MB limit"},
        status_code=413,
    )


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """Rejects any request body exceeding MAX_BODY_BYTES before it's read
    into a Pydantic model. /api/upload has its own streaming size check for
    the multipart path; this covers the JSON-body endpoints (/api/spanner,
    /api/compare, /api/trends, ...), which previously had no size guard at
    all.

    A declared Content-Length is checked first (cheap, no body read). But a
    client can omit Content-Length entirely (e.g. chunked
    Transfer-Encoding), which used to skip the check completely -- so when
    it's absent, the body is streamed and counted directly, then cached
    onto the request so the downstream handler still sees it (see the
    `_body` comment in dispatch()).
    """

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > MAX_BODY_BYTES:
                    return _too_large_response()
            except ValueError:
                pass
            return await call_next(request)

        # No Content-Length (e.g. chunked Transfer-Encoding) -- stream and
        # count so these clients can't bypass the limit. Starlette's
        # BaseHTTPMiddleware wraps `request` in a _CachedRequest whose
        # wrapped_receive() replays `request._body` to the downstream
        # handler *only* if it was populated via body()/this same
        # attribute -- calling request.stream() and then call_next()
        # without this would leave the downstream handler seeing an empty
        # body, since _CachedRequest deliberately doesn't re-stream what
        # was already consumed by a call to .stream().
        chunks: list[bytes] = []
        total = 0
        async for chunk in request.stream():
            total += len(chunk)
            if total > MAX_BODY_BYTES:
                return _too_large_response()
            chunks.append(chunk)
        request._body = b"".join(chunks)
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
            # `if h` alone only drops IPs that some *other* request already
            # emptied via the sliding-window pop above -- a one-shot IP
            # that never comes back keeps a non-empty (but fully expired)
            # deque forever, since nothing ever revisits it to prune it.
            # Evict by each IP's own most recent hit (h[-1]) against the
            # window instead, so idle IPs actually get reclaimed.
            self._hits = defaultdict(deque, {
                ip: h for ip, h in self._hits.items()
                if h and now - h[-1] <= RATE_LIMIT_WINDOW_SECONDS
            })
        return await call_next(request)
