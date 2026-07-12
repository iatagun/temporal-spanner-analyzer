import asyncio
import time

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from backend.middleware import MaxBodySizeMiddleware, RateLimitMiddleware
from backend.main import app as real_app


async def _echo(request):
    body = await request.body()
    return PlainTextResponse(f"len={len(body)}")


def test_rate_limit_returns_429_after_limit_exceeded():
    # Isolated Starlette app (not backend.main.app) so this doesn't share
    # request-count state with the rest of the test suite.
    app = Starlette(routes=[Route("/", _echo)])
    app.add_middleware(RateLimitMiddleware, requests_per_minute=3)
    client = TestClient(app)

    for _ in range(3):
        assert client.get("/").status_code == 200
    r = client.get("/")
    assert r.status_code == 429


def test_rate_limit_exempts_health_path():
    app = Starlette(routes=[Route("/api/health", _echo)])
    app.add_middleware(RateLimitMiddleware, requests_per_minute=1)
    client = TestClient(app)

    for _ in range(5):
        assert client.get("/api/health").status_code == 200


def test_rate_limit_disabled_when_zero():
    app = Starlette(routes=[Route("/", _echo)])
    app.add_middleware(RateLimitMiddleware, requests_per_minute=0)
    client = TestClient(app)

    for _ in range(10):
        assert client.get("/").status_code == 200


def _fake_request(client_ip: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "headers": [],
        "client": (client_ip, 1),
        "query_string": b"",
    }

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(scope, receive)


def test_rate_limit_evicts_expired_idle_ips(monkeypatch):
    # Regression test: the periodic prune only dropped IPs whose deque was
    # already empty, which only happens when *that same IP* makes another
    # request. A one-shot IP whose entire deque has aged out of the window
    # but never comes back used to survive forever.
    monkeypatch.setattr("backend.middleware._MAX_TRACKED_IPS", 2)
    mw = RateLimitMiddleware(app=None, requests_per_minute=100)

    long_ago = time.monotonic() - 1000  # long past RATE_LIMIT_WINDOW_SECONDS
    mw._hits["stale-ip-1"].append(long_ago)
    mw._hits["stale-ip-2"].append(long_ago)
    assert len(mw._hits) == 2

    async def call_next(request):
        return PlainTextResponse("ok")

    # This request pushes len(_hits) to 3, past _MAX_TRACKED_IPS=2, which
    # triggers the periodic eviction pass inside dispatch().
    asyncio.run(mw.dispatch(_fake_request("fresh-ip"), call_next))

    assert "stale-ip-1" not in mw._hits
    assert "stale-ip-2" not in mw._hits
    assert "fresh-ip" in mw._hits


def test_max_body_size_rejects_large_content_length():
    app = Starlette(routes=[Route("/", _echo, methods=["POST"])])
    app.add_middleware(MaxBodySizeMiddleware)
    client = TestClient(app)

    r = client.post("/", content=b"x" * 10, headers={"content-length": str(100 * 1024 * 1024)})
    assert r.status_code == 413


def test_spanner_endpoint_rejects_oversized_json_body(monkeypatch):
    # Regression test: /api/spanner, /api/compare, /api/trends previously
    # had no request-body size guard at all (only /api/upload's multipart
    # path did) -- a client could POST an arbitrarily large graph directly.
    monkeypatch.setattr("backend.middleware.MAX_BODY_BYTES", 100)
    client = TestClient(real_app)
    g = {"vertices": ["a", "b"], "edges": [{"u": "a", "v": "b", "label": 1.0}] * 50}
    r = client.post("/api/spanner", json={"graph": g})
    assert r.status_code == 413


def test_max_body_size_rejects_when_content_length_header_missing(monkeypatch):
    # Regression test: the size guard only inspected the Content-Length
    # header; a request sent without one (e.g. chunked Transfer-Encoding)
    # skipped the check entirely and reached the handler uncapped. Drive
    # the ASGI app directly so no Content-Length header is ever set (a
    # normal httpx/TestClient POST always adds one).
    monkeypatch.setattr("backend.middleware.MAX_BODY_BYTES", 100)
    app = Starlette(routes=[Route("/", _echo, methods=["POST"])])
    app.add_middleware(MaxBodySizeMiddleware)

    big_body = b"x" * 1000
    chunks = [
        {"type": "http.request", "body": big_body[:500], "more_body": True},
        {"type": "http.request", "body": big_body[500:], "more_body": False},
    ]

    async def receive():
        return chunks.pop(0)

    sent = []

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],  # deliberately no content-length
        "client": ("testclient", 123),
        "server": ("testserver", 80),
    }

    asyncio.run(app(scope, receive, send))

    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    assert status == 413


def test_max_body_size_allows_small_body_when_content_length_missing():
    app = Starlette(routes=[Route("/", _echo, methods=["POST"])])
    app.add_middleware(MaxBodySizeMiddleware)

    chunks = [{"type": "http.request", "body": b"hello", "more_body": False}]

    async def receive():
        return chunks.pop(0)

    sent = []

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
        "client": ("testclient", 123),
        "server": ("testserver", 80),
    }

    asyncio.run(app(scope, receive, send))

    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    body = b"".join(m["body"] for m in sent if m["type"] == "http.response.body")
    assert status == 200
    assert body == b"len=5"
