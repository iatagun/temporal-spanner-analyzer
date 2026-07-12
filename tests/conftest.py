import os

# The full test suite fires far more than 30 requests (the production
# RateLimitMiddleware default) against the single shared `backend.main.app`
# instance within a couple of seconds -- without this, the suite itself
# would start tripping its own rate limiter. Must be set before
# backend.middleware is first imported (it reads this as a class-default
# at import time), so this lives in conftest.py, which pytest loads before
# collecting/importing any test module.
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "100000")
