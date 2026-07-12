from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from backend.middleware import MaxBodySizeMiddleware, RateLimitMiddleware
from backend.main import app as real_app


async def _echo(request):
    return PlainTextResponse("ok")


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
