import logging
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("temporal_spanner")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.middleware import MaxBodySizeMiddleware, RateLimitMiddleware
from backend.routers import spanner, trends, compare, explore

app = FastAPI(title="Temporal Spanner API", version="0.1.0")

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:3004,http://127.0.0.1:3004"
    ).split(",")
    if origin.strip()
]

# Registration order matters: Starlette wraps middleware so the *last*
# one added is outermost. CORSMiddleware must be added last so it still
# runs (and attaches CORS headers) even when RateLimit/MaxBodySize
# short-circuit a request with a 429/413 -- otherwise the frontend's
# fetch() can't read the error body cross-origin at all.
app.add_middleware(RateLimitMiddleware)
app.add_middleware(MaxBodySizeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def log_unhandled_exceptions(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse({"detail": "Internal server error"}, status_code=500)


app.include_router(spanner.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(explore.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "algo": "Baligács 2026"}
